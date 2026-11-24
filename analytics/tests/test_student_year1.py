"""Independent dataset grain, exposure and missingness fixtures."""

import sqlite3
from types import SimpleNamespace

import pytest

from analytics.exploration.datasets import ExplorationRefusal, build
from measures.requests import Filters
from measures.tests.explorer_fixture import here, make_database, student


def source(path):
    """Borrow a fixture connection in the same named/positional forms as production."""
    named = sqlite3.connect(path)
    named.row_factory = sqlite3.Row
    positional = sqlite3.connect(path)
    return SimpleNamespace(named=named, positional=positional)


def test_composite_grain_attempts_and_independent_credits(tmp_path):
    """Repeated attempts count; another cohort cannot contribute credits or exposure."""
    path = make_database(tmp_path / 'data.db', [
        student('private-a', earned=10, attempted=20, retention=1),
        student('private-a', cohort='2022-23', earned=30, attempted=40),
        student('private-b', earned=None, attempted=40),
        student('private-c', earned=30, attempted=40, retention=0),
    ], [
        here('private-a', '2023-24', 'FALL', delivery='O', earned=999),
        here('private-a', '2023-24', 'FALL', delivery='O'),
        here('private-a', '2022-23', 'FALL', cohort='2022-23', delivery='O'),
        here('private-c', '2023-24', 'FALL', delivery='F'),
    ])
    snapshot = source(path)
    try:
        data = build(snapshot, '2023-24', Filters())
        assert len(data.rows) == 3
        a, b, c = data.rows
        assert (a.credits_earned_y1, a.credits_attempted_y1) == (10, 20)
        assert (a.online_enrollment_count_y1, a.online_enrollment_share_y1) == (2, 1)
        assert b.online_enrollment_count_y1 is None
        assert b.online_reasons == ('no_year1_records',)
        assert b.credits_attempted_y1 == 40 and b.credits_earned_y1 is None
        assert c.online_enrollment_count_y1 == 0 and c.online_enrollment_share_y1 == 0
        assert c.retained_school == 0
        assert a.retained_federal is None
        assert a.retained_federal_reason == 'not_yet_observable'
        assert 'private-a' not in repr(data)
        assert 'not certified' in data.coverage
    finally:
        snapshot.named.close()
        snapshot.positional.close()


@pytest.mark.parametrize('n', range(1, 10))
def test_sparse_groups_filters_and_bad_observation(tmp_path, monkeypatch, n):
    """Obsolete thresholds never remove small units or turn unknown exposure into zero."""
    monkeypatch.setenv('UNCF_MIN_STUDENTS', '100')
    path = make_database(tmp_path / 'data.db', [student(str(i), pell='Y') for i in range(n)],
        [here('0', '2023-24', 'FALL', delivery=None)])
    snapshot = source(path)
    try:
        data = build(snapshot, '2023-24', Filters(pell='Y'))
        assert len(data.rows) == n
        assert data.rows[0].online_reasons == ('unknown_delivery',)
        snapshot.named.execute('UPDATE course_enrollment SET term_id = NULL')
        assert set(build(snapshot, '2023-24', Filters()).rows[0].online_reasons) == {'no_year1_records', 'unresolved_term'}
    finally:
        snapshot.named.close()
        snapshot.positional.close()


def test_duplicate_membership_is_not_a_course_join(tmp_path):
    """Identical membership duplicates deduplicate and conflicting credits refuse."""
    path = make_database(tmp_path / 'data.db', [student('a', earned=10)],
        [here('a', '2023-24', 'FALL', delivery='H')])
    snapshot = source(path)
    try:
        snapshot.named.executescript('ALTER TABLE cohort_membership RENAME TO original; CREATE TABLE cohort_membership AS SELECT * FROM original; INSERT INTO cohort_membership SELECT * FROM original;')
        data = build(snapshot, '2023-24', Filters())
        assert len(data.rows) == 1 and data.rows[0].online_enrollment_count_y1 == 0
        snapshot.named.execute('UPDATE cohort_membership SET number_of_credits_earned_yr_1 = 20 WHERE rowid = 2')
        with pytest.raises(ExplorationRefusal):
            build(snapshot, '2023-24', Filters())
    finally:
        snapshot.named.close()
        snapshot.positional.close()


@pytest.mark.parametrize('value', [-1, float('inf'), 'invalid'])
def test_invalid_credit_metadata_is_rejected(tmp_path, value):
    """Invalid values are validation failures, never substituted zeros."""
    path = make_database(tmp_path / 'data.db', [student('a', earned=value)])
    snapshot = source(path)
    try:
        with pytest.raises(ValueError):
            build(snapshot, '2023-24', Filters())
    finally:
        snapshot.named.close()
        snapshot.positional.close()


def test_unknown_retention_is_distinct_from_unobserved_federal(tmp_path):
    """Observed next fall supports a real federal zero independently of school unknown."""
    path = make_database(tmp_path / 'data.db', [student('a'), student('b')],
        [here('b', '2024-25', 'FALL', delivery='F')])
    snapshot = source(path)
    try:
        a, b = build(snapshot, '2023-24', Filters()).rows
        assert a.retained_school is None and a.retained_school_reason == 'unknown'
        assert a.retained_federal == 0 and b.retained_federal == 1
        assert a.retained_federal_reason is None
        assert not build(snapshot, '2023-24', Filters(pell='N')).rows
    finally:
        snapshot.named.close()
        snapshot.positional.close()


def test_unknown_year_does_not_become_known_zero(tmp_path):
    """An unresolved year invalidates exposure even beside a valid face-to-face record."""
    path = make_database(tmp_path / 'data.db', [student('a')],
        [here('a', '2023-24', 'FALL', delivery='F'), here('a', '2024-25', 'FALL', delivery='O')])
    snapshot = source(path)
    try:
        snapshot.named.execute("UPDATE term SET academic_year='UNKNOWN' WHERE academic_year='2024-25'")
        row = build(snapshot, '2023-24', Filters()).rows[0]
        assert row.online_enrollment_count_y1 is None
        assert row.online_reasons == ('unresolved_term',)
    finally:
        snapshot.named.close()
        snapshot.positional.close()
