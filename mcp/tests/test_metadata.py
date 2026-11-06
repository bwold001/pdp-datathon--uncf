"""A Metadata serves one snapshot of the repo's files: the checksums it reports are of the bytes its answers come
from, however the files change on disk after it reads them. A new Metadata reads the files again.

Each test works on a copy of the metadata files in a temporary folder, never the repo's own.
"""

import hashlib
import shutil

import pytest

from conftest import MODEL_DIR, REPO
from pdp_mcp.metadata import Metadata

ADDED_TABLE = "\nzz_added:\n  a: {type: str, nullable: true}\n"


@pytest.fixture
def root(tmp_path):
    shutil.copytree(MODEL_DIR / "config", tmp_path / "normalized-data-model/config")
    shutil.copy(MODEL_DIR / "README.md", tmp_path / "normalized-data-model/README.md")
    shutil.copytree(REPO / "data/dictionaries", tmp_path / "data/dictionaries")
    return tmp_path


def schema_file(root):
    return root / "normalized-data-model/config/destination_schema.yaml"


def checksums(metadata):
    problem, files = metadata.status()
    assert problem is None
    return {f["path"]: f["sha256"] for f in files}


def test_the_checksums_are_of_the_files_the_definitions_came_from(root):
    metadata = Metadata(root)
    reported = checksums(metadata)
    assert reported == {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in reported}
    assert len(reported) == 9 and len(metadata.tables()) == 10


@pytest.mark.parametrize("first", ["status", "tables"])
def test_a_file_changed_later_changes_neither_the_checksums_nor_the_definitions(root, first):
    """Whichever is asked first, a change on disk afterwards reaches neither: they stay one snapshot."""
    metadata = Metadata(root)
    before = checksums(metadata) if first == "status" else None
    tables = [t["name"] for t in metadata.tables()]
    before = before or checksums(metadata)
    schema_file(root).write_text(schema_file(root).read_text() + ADDED_TABLE)
    assert checksums(metadata) == before
    assert [t["name"] for t in metadata.tables()] == tables and "zz_added" not in tables
    assert metadata.status()[0] is None


def test_a_change_before_the_first_answer_is_in_the_snapshot_with_its_checksum(root):
    """The snapshot is taken on first use, all files at once: a change before it is in both."""
    metadata = Metadata(root)
    schema_file(root).write_text(schema_file(root).read_text() + ADDED_TABLE)
    assert "zz_added" in [t["name"] for t in metadata.tables()]
    path = "normalized-data-model/config/destination_schema.yaml"
    assert checksums(metadata)[path] == hashlib.sha256(schema_file(root).read_bytes()).hexdigest()


def test_a_new_metadata_reads_the_changed_files(root):
    old = Metadata(root)
    old_checksums = checksums(old)
    schema_file(root).write_text(schema_file(root).read_text() + ADDED_TABLE)
    new = Metadata(root)
    path = "normalized-data-model/config/destination_schema.yaml"
    assert checksums(new)[path] != old_checksums[path]
    assert checksums(new)[path] == hashlib.sha256(schema_file(root).read_bytes()).hexdigest()
    assert "zz_added" in [t["name"] for t in new.tables()] and len(new.tables()) == 11


def test_a_missing_file_is_reported_without_a_checksum(root):
    schema_file(root).unlink()
    problem, files = Metadata(root).status()
    assert problem == "can't read normalized-data-model/config/destination_schema.yaml"
    assert {f["path"]: f["sha256"] for f in files}["normalized-data-model/config/destination_schema.yaml"] is None
    assert len(files) == 9


def test_a_missing_loader_config_is_reported(root):
    (root / "normalized-data-model/config/pipeline.yaml").unlink()
    problem, files = Metadata(root).status()
    assert problem.startswith("can't read normalized-data-model/config/pipeline.yaml") and files == []


def test_a_file_that_cant_be_parsed_is_reported_with_its_checksum(root):
    schema_file(root).write_text("student: [unclosed\n")
    problem, files = Metadata(root).status()
    assert problem.startswith("a metadata file can't be parsed")
    assert all(f["sha256"] for f in files)


def test_a_running_servers_database_info_matches_what_its_tools_serve(root):
    """Codex's case on PR #63: a file changes while the server runs. get_database_info keeps the checksums and table
    count of the definitions the other tools still answer from."""
    from pdp_mcp.config import Settings
    from pdp_mcp.server import Tools
    tools = Tools(Settings(), Metadata(root))
    names = [t.name for t in tools.list_tables().tables]
    before = tools.get_database_info().metadata
    schema_file(root).write_text(schema_file(root).read_text() + ADDED_TABLE)
    after = tools.get_database_info().metadata
    assert after.files == before.files and after.table_count == before.table_count == len(names) == 10
    assert [t.name for t in tools.list_tables().tables] == names
