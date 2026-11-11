"""Real SQLite transactions establish the shared-snapshot and cleanup contract."""

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from analytics.coverage import Coverage
from analytics.data_access import SnapshotStep, _postgres_query, connection_snapshot, run_snapshot_steps, sqlite_snapshot
from analytics.execution import execution_scope
from analytics.provenance import DataUnavailable, VersionUnavailable
from analytics.service import AnalyticsService
from measures.breakdowns.credit_momentum import credit_momentum
from measures.breakdowns.dfw_courses import dfw_course, dfw_courses
from measures.breakdowns.gateway_courses import gateway_courses
from measures.breakdowns.student_paths import student_paths
from measures.models import Cohort, Group, GroupDimension, Measure
from measures.run_measures import run_measure
from measures.tests.explorer_fixture import here, make_database, student


def add_identity(path, generation="00000000-0000-4000-8000-000000000001"):
    """Install an explicitly synthetic build manifest, not a certification of source data."""
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS load_run (build_manifest TEXT)")
        db.execute("DELETE FROM load_run")
        db.execute("INSERT INTO load_run VALUES (?)", [json.dumps({"schema_version": 1,
            "load_generation": generation, "pipeline_version": "a" * 64, "normalization_digest": "b" * 64})])
        db.execute("UPDATE data_provider SET file_sha256 = ?", ["c" * 64])


@pytest.fixture
def database(tmp_path):
    """Twelve synthetic entrants, six retained, with known credits and a course each."""
    students = [student(f"s{i}", retention=int(i < 6), attempted=12, earned=6) for i in range(12)]
    records = [here(f"s{i}", "2023-24", "FALL", grade="2.0", attempted=12, earned=6, gateway="E") for i in range(12)]
    path = make_database(tmp_path / "snapshot.sqlite", students, records)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("ALTER TABLE cohort_membership ADD COLUMN program_of_study_term_1 TEXT")
        db.execute("UPDATE cohort_membership SET program_of_study_term_1 = '400501'")
    add_identity(path)
    return path


def test_named_and_positional_views_share_one_pinned_snapshot(database):
    """Reloads cannot give two steps different generations or retention values."""
    service = AnalyticsService(database, Coverage(suppression_threshold=1))
    with sqlite_snapshot(database) as snapshot:
        first = snapshot.identity
        (measure,) = run_measure(Measure.RETENTION, [Cohort.of("2023-24")], database=snapshot.positional)
        with sqlite3.connect(database) as writer:
            writer.execute("UPDATE cohort_membership SET retention=0")
        add_identity(database, "00000000-0000-4000-8000-000000000002")
        legacy = service.for_snapshot(snapshot).analyze({"analysis": "retention", "cohort": "2023-24"})
        assert (measure.numerator, measure.denominator) == (6, 12)
        assert legacy.receipts[0].rows[0].rate == .5
        assert snapshot.identity == first
        assert dict(snapshot.named.execute("SELECT COUNT(*) AS n FROM cohort_membership").fetchone()) == {"n": 12}
        assert tuple(snapshot.positional.execute("SELECT COUNT(*) FROM cohort_membership").fetchone()) == (12,)
    with sqlite_snapshot(database) as second:
        assert second.identity.snapshot_ref != first.snapshot_ref
        assert second.named.execute("SELECT SUM(retention) AS n FROM cohort_membership").fetchone()["n"] == 0


@pytest.mark.parametrize("page,extra", [(dfw_courses, {}), (dfw_course, {"course": "ENG 101"}),
    (credit_momentum, {}), (gateway_courses, {}), (student_paths, {})])
def test_page_wrappers_preserve_values_and_borrow_snapshot(database, page, extra):
    """Every page reuses its caller's source and leaves it open for subsequent work."""
    expected = page("2023-24", database=database, **extra)
    with sqlite_snapshot(database) as snapshot:
        actual = page("2023-24", snapshot=snapshot, **extra)
        assert actual == expected
        assert snapshot.named.execute("SELECT 1 AS n").fetchone()["n"] == 1
    with pytest.raises(DataUnavailable):
        snapshot.named.execute("SELECT 1")


@pytest.mark.parametrize("page", [credit_momentum, gateway_courses, student_paths, dfw_courses])
@pytest.mark.parametrize("threshold,status", [(None, "ok"), ("10", "ok")])
def test_small_groups_follow_setting_inside_borrowed_snapshot(database, monkeypatch, page, threshold, status):
    """Three synthetic students stay visible by default without losing snapshot ownership or configured hiding."""
    monkeypatch.delenv("UNCF_MIN_STUDENTS", raising=False)
    if threshold is not None:
        monkeypatch.setenv("UNCF_MIN_STUDENTS", threshold)
    with sqlite3.connect(database) as writer:
        writer.execute("UPDATE cohort_membership SET pell_status_first_year='N' WHERE student_id NOT IN ('s0', 's1', 's2')")
    filters = Group.of((GroupDimension.PELL, "Y"))
    with sqlite_snapshot(database) as snapshot:
        # Commit new values after pinning the read snapshot; every page must retain the old answers.
        with sqlite3.connect(database) as writer:
            writer.execute("UPDATE cohort_membership SET retention=0, number_of_credits_earned_yr_1=0")
        result = page("2023-24", filters=filters, snapshot=snapshot)
        assert result["status"] == status
        if status == "ok":
            if page is dfw_courses:
                assert result["everyone"]["students"] == 3
                assert result["courses"][0]["students"] == 3
            else:
                assert result["students"] == 3
            if page is credit_momentum:
                assert result["credits"]["avg_earned"] == 6
                assert result["retention"]["rate"] == 1
                assert result["progress"] is not None
            if page is gateway_courses:
                assert result["courses"][0]["students"] == 3
                assert result["context"]["min_pair_students"] == 1
        elif page is credit_momentum:
            assert result["progress"] is None
        assert snapshot.positional.execute("SELECT SUM(retention) FROM cohort_membership").fetchone() == (6,)


def test_writes_poison_the_session_and_cleanup_finishes(database):
    """A database error cannot silently continue work or leave a lock behind."""
    with sqlite_snapshot(database) as snapshot:
        with pytest.raises(DataUnavailable):
            snapshot.named.execute("DELETE FROM cohort_membership")
        with pytest.raises(DataUnavailable):
            snapshot.named.execute("SELECT 1")
    with sqlite3.connect(database, timeout=.01) as writer:
        assert writer.execute("SELECT COUNT(*) FROM cohort_membership").fetchone() == (12,)
        writer.execute("UPDATE cohort_membership SET retention=0")


def test_owner_rolls_back_and_closes_before_return_without_changing_global_row_factory(database):
    """Track actual driver cleanup on failure; WAL writer availability alone cannot prove closure."""
    events = []

    class TrackedConnection(sqlite3.Connection):
        """Expose cleanup order without replacing real SQLite query behavior."""

        def rollback(self):
            """Record transaction release before connection close."""
            events.append("rollback")
            return super().rollback()

        def close(self):
            """Record actual closure before control returns to the batch caller."""
            events.append("close")
            return super().close()

    raw = sqlite3.connect(database, factory=TrackedConnection)
    raw.row_factory = sqlite3.Row

    def fail(snapshot):
        """Read both views before deliberately triggering a real database failure."""
        assert snapshot.named.cursor().execute("SELECT 7 AS value").fetchone() == {"value": 7}
        assert snapshot.positional.cursor().execute("SELECT 7").fetchone() == (7,)
        assert raw.row_factory is sqlite3.Row
        snapshot.named.execute("SELECT missing_column FROM student")

    batch = run_snapshot_steps(lambda: connection_snapshot(raw), (SnapshotStep("failed", fail),))
    assert batch.failure.code == "data_unavailable"
    assert events == ["rollback", "close"]
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        raw.execute("SELECT 1")


def test_snapshot_refuses_cross_thread_use(database):
    """One transaction cannot migrate between concurrently running worker threads."""
    with sqlite_snapshot(database) as snapshot, ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(DataUnavailable, match="thread"):
            pool.submit(snapshot.named.execute, "SELECT 1").result()
        assert snapshot.positional.execute("SELECT 1").fetchone() == (1,)


def test_timeout_preserves_completed_work_stops_later_steps_and_releases_locks(database):
    """The batch returns partial internal evidence only after rollback and close."""
    ran = []

    def expensive(snapshot):
        """Run trusted SQL intentionally longer than the synthetic request budget."""
        return snapshot.named.execute("WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM seq WHERE n<1000000000) SELECT SUM(n) FROM seq").fetchone()

    with execution_scope(.04):
        batch = run_snapshot_steps(lambda: sqlite_snapshot(database), (
            SnapshotStep("first", lambda s: s.positional.execute("SELECT COUNT(*) FROM cohort_membership").fetchone()[0]),
            SnapshotStep("slow", expensive), SnapshotStep("last", lambda s: ran.append(True))))
    assert batch.completed == (("first", 12),)
    assert batch.failure.code == "timeout" and batch.failure.step_id == "slow"
    assert batch.not_executed == ("last",) and ran == []
    with sqlite3.connect(database, timeout=.01) as writer:
        writer.execute("UPDATE cohort_membership SET retention=0")


def test_explicit_source_missing_or_legacy_metadata_never_silently_falls_back(tmp_path, database):
    """V2 requires persisted provenance, while v1 remains usable on old extracts."""
    with pytest.raises(DataUnavailable), sqlite_snapshot(tmp_path / "missing.sqlite"):
        pass
    with sqlite3.connect(database) as writer:
        writer.execute("DROP TABLE load_run")
    with pytest.raises(VersionUnavailable), sqlite_snapshot(database):
        pass
    assert AnalyticsService(database, Coverage(suppression_threshold=1)).analyze({"analysis": "retention", "cohort": "2023-24"}).receipts[0].rows[0].rate == .5


def test_each_batch_has_a_separate_execution_identity(database):
    """Run IDs change independently of stable snapshot identity."""
    calls = (SnapshotStep("count", lambda s: s.positional.execute("SELECT 1").fetchone()[0]),)
    one = run_snapshot_steps(lambda: sqlite_snapshot(database), calls)
    two = run_snapshot_steps(lambda: sqlite_snapshot(database), calls)
    assert one.execution_id != two.execution_id and one.identity == two.identity


def test_fixed_query_placeholder_translation_keeps_literals_and_comments():
    """Driver bindings must not replace question marks inside fixed SQL text."""
    assert _postgres_query("SELECT '?' AS marker, ? AS value -- ?\n/* ? */", (7,)) == "SELECT '?' AS marker, %s AS value -- ?\n/* ? */"
    assert _postgres_query("SELECT '50%' AS share, ? AS value", (7,)) == "SELECT '50%%' AS share, %s AS value"


def test_provider_order_is_not_a_snapshot_identity_input(database):
    """Surrogate provider IDs do not replace the sorted logical manifest."""
    with sqlite_snapshot(database) as first:
        identity = first.identity
    with sqlite3.connect(database) as writer:
        writer.execute("UPDATE data_provider SET provider_id=99")
    with sqlite_snapshot(database) as second:
        assert identity == second.identity


def test_database_error_stops_independent_following_work(database):
    """A poisoned transaction is never reopened to finish the remainder on newer data."""
    later = []
    batch = run_snapshot_steps(lambda: sqlite_snapshot(database), (
        SnapshotStep("first", lambda s: s.positional.execute("SELECT 1").fetchone()[0]),
        SnapshotStep("broken", lambda s: s.named.execute("SELECT missing FROM nonexistent")),
        SnapshotStep("last", lambda s: later.append(True))))
    assert batch.completed == (("first", 1),) and batch.failure.code == "data_unavailable"
    assert batch.not_executed == ("last",) and later == []


def test_batch_validates_step_limits_before_opening_a_database():
    """Malformed batches cannot acquire a transaction or execute any callbacks."""
    def forbidden():
        """Any attempt to open a source means validation ran too late."""
        raise AssertionError("opened source")

    with pytest.raises(ValueError):
        run_snapshot_steps(forbidden, (SnapshotStep("duplicate", None),) * 2)
