"""Checks the precompute helpers."""
from api.precompute import group_bys
from measures.models import GroupDimension


def test_group_bys_skip_first_gen_and_course() -> None:
    """Singles plus pairs, never first-gen or the DFW-only course."""
    groups = group_bys()
    used = {d for g in groups for d in g.dimensions}
    assert GroupDimension.FIRST_GEN not in used
    assert GroupDimension.COURSE not in used
    assert len(groups) == 36


def test_precompute_saves_each_measure_in_one_call(monkeypatch) -> None:
    """Each measure gets one save with every cohort and group, so one save can't wipe another."""
    from api import precompute as module

    calls = []
    monkeypatch.setattr(module, "run_measure", lambda *args, **kwargs: calls.append((args, kwargs)) or [])
    module.precompute()
    assert [args[0] for args, _ in calls] == module.MEASURES
    for args, kwargs in calls:
        assert len(args[1]) == 4 and len(args[2]) == 36
        assert kwargs["save"] is True
