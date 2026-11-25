"""The chat's instructions name the kind of data the evidence comes from (UNCF_DATA_LABEL)."""

from app.chat import v2


def test_instructions_say_synthetic_on_the_sample(monkeypatch):
    """Unset, the model is told the evidence is synthetic."""
    monkeypatch.delenv("UNCF_DATA_LABEL", raising=False)
    assert v2.rules().endswith("All evidence is synthetic.\n")


def test_instructions_name_the_schools_files_on_real_data(monkeypatch):
    """With a school's files, the model is never told the evidence is synthetic."""
    monkeypatch.setenv("UNCF_DATA_LABEL", "institution")
    text = v2.rules()
    assert "synthetic" not in text.lower()
    assert text.endswith("Evidence comes from the institution's own PDP files.\n")
