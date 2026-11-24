"""Independent arithmetic and refusal tests for registered exploration."""

import json
from dataclasses import replace

import pytest
from pydantic import ValidationError

from analytics.contracts_v2 import CorrelationParameters, GroupedParameters
from analytics.disclosure import disclose_plan, stage_defined
from analytics.exploration.adapters import adapt
from analytics.exploration.datasets import Dataset, ExplorationRefusal, StudentYear1
from analytics.exploration.operations import _correlation, _grouped, bound_groups, execute
from analytics.execution import CalculationCancelled


def row(i, earned=None, attempted=None, online=None, retained=None):
    """Build an internal synthetic unit without deriving expectations from production code."""
    return StudentYear1(str(i), '2023-24', earned, attempted, online, None, retained, None,
        'unknown' if retained is None else None, 'not_yet_observable',
        ('no_year1_records',) if online is None else ())


def grouped(rows, comparison=False, grouping='online_count_0_1to2_3plus'):
    """Invoke the pure statistical owner with an independent unlimited test deadline."""
    return _grouped(Dataset(tuple(rows), 0), GroupedParameters(cohort='2023-24', grouping=grouping), comparison, float('inf'))


def paired(rows, x='online_enrollment_count_y1', y='credits_earned_y1'):
    """Calculate a registered pair from a known tiny dataset."""
    return _correlation(Dataset(tuple(rows), 0), CorrelationParameters(cohort='2023-24', x=x, y=y), float('inf'))


def test_separate_eligible_means_and_exact_ordered_differences():
    """Earned mean 20/n2 differs from attempted 100/3/n3; n1 differences stay valid."""
    rows = [row(0, 10, 20, 0), row(1, None, 40, 0), row(2, 30, 40, 0), row(3, 15, 25, 1), row(4, 5, 10, 3)]
    evidence = grouped(rows)
    first = evidence.result.payload.rows[0].cells
    assert first == ('zero', 3, 20, 2, 1, 100 / 3, 3, 0)
    comparison = grouped(rows, True).result.payload
    assert [(d.minuend, d.subtrahend, d.value, d.minuend_n, d.subtrahend_n) for d in comparison.differences] == [
        ('one_to_two', 'zero', -5, 1, 2), ('three_plus', 'zero', -15, 1, 2), ('three_plus', 'one_to_two', -10, 1, 1)]


def test_missing_group_mean_preserves_siblings():
    """Missing earned credits retain an occupied group and all valid comparisons."""
    payload = grouped([row(0, 10, 20, 0), row(1, None, 40, 1), row(2, 30, None, 3)], True).result.payload
    assert payload.groups[1].n == 0 and payload.groups[1].missing_count == 1
    assert [d.value for d in payload.differences] == [None, 20, None]
    assert payload.differences[0].unavailable_reason == 'missing_group_mean'


@pytest.mark.parametrize('threshold', ['10', '100'])
@pytest.mark.parametrize('n', range(1, 10))
def test_serialized_small_groups_and_policy_projection(n, threshold, monkeypatch):
    """Actual aggregate JSON preserves each sparse group and one-unit exclusions."""
    monkeypatch.setenv('UNCF_MIN_STUDENTS', threshold)
    evidence = grouped([row(i, 12, 20, 0) for i in range(n)] + [row('excluded', 99, 99)])
    from analytics.exploration.operations import OPERATIONS

    owner = adapt('grouped_summary', evidence)
    stage = stage_defined("summary", OPERATIONS["grouped_summary"], owner)
    projected = disclose_plan((stage,))[0].result
    payload = json.loads(projected.model_dump_json())
    assert payload['payload']['rows'][0]['cells'] == ['zero', n, 12, n, 0, 20, n, 0]
    assert payload['exclusions'] == [{'reason': 'no_year1_records', 'count': 1}]
    assert 'student_id' not in owner.model_dump_json() and 'excluded' not in payload['payload']['rows'][0]['cells']


@pytest.mark.parametrize('sign', [1, -1])
def test_pearson_two_pairs_and_unrelated_missingness(sign):
    """Two varying pairs give exactly +1/-1 despite missing attempted credits."""
    evidence = paired([row(0, 10 * sign, online=0), row(1, 20 * sign, online=1), row(2, None, online=3)])
    payload = evidence.result.payload
    assert payload.n == 2 and payload.coefficient == sign
    assert evidence.result.exclusions[0].count == 1


def test_correlation_limits_and_retention_directions():
    """Insufficient pairs and zero variance remain different unavailable states."""
    assert paired([row(0, 1, online=0)]).result.reason == 'no_evidence'
    assert paired([row(0, 1, online=0), row(1, 1, online=1)]).result.reason == 'zero_variance'
    result = grouped([row(0, 10, retained=1), row(1, 30, retained=0), row(2)], True,
        'retention_outcome_school').result
    assert result.payload.differences[0].value == 20
    assert result.payload.differences[0].minuend == 'not_retained'
    assert [(e.reason, e.count) for e in result.exclusions] == [('unknown', 1)]


def test_empty_and_unknown_federal():
    """Unobserved federal answers cannot be folded into not retained."""
    assert grouped([]).result.status == 'unavailable'
    result = grouped([row(0, 10)], grouping='retention_outcome_federal')
    assert result.result.status == 'unavailable'


def test_resource_limits_without_truncation(monkeypatch):
    """Twenty occupied singleton groups pass, twenty-one refuse; expired steps stop."""
    bound_groups({str(i): [i] for i in range(20)})
    bound_groups({**{str(i): [i] for i in range(20)}, 'empty': []})
    with pytest.raises(ExplorationRefusal, match='limit_exceeded'):
        bound_groups({str(i): [i] for i in range(21)})
    with pytest.raises(CalculationCancelled):
        _grouped(Dataset((row(0, 1, 1, 0),), 0), GroupedParameters(cohort='2023-24', grouping='online_count_0_1to2_3plus'), False, 0)
    monkeypatch.setattr('analytics.exploration.operations.STEP_SECONDS', 0)
    with pytest.raises(CalculationCancelled):
        execute('grouped_summary', {'cohort': '2023-24', 'grouping': 'online_count_0_1to2_3plus'}, None)


@pytest.mark.parametrize('extra', [{'sql': 'SELECT 1'}, {'group_by': ['pell', 'gender']}, {'threshold': 2}, {'missing_policy': 'zero'}])
def test_strict_requests(extra):
    """Expressions, extra fields and alternative missing rules cannot reach an executor."""
    with pytest.raises(ValidationError):
        GroupedParameters.model_validate({'cohort': '2023-24', 'grouping': 'online_count_0_1to2_3plus', **extra})
    with pytest.raises(ValidationError):
        CorrelationParameters(cohort='2023-24', x='online_enrollment_count_y1', y='online_enrollment_share_y1')


def test_gateway_variant_is_honestly_unavailable():
    """Unsupported equivalence returns evidence, not a substituted first-attempt result."""
    evidence = execute('measure_variant', {'cohort': '2023-24', 'variant_id': 'gateway.cohort_completion_c_or_better'}, None)
    assert evidence.result.reason == 'unsupported_evidence'
    assert 'highest' in ' '.join(evidence.context)


def test_nonfinite_inputs_refuse():
    """Pure executors also reject nonfinite metadata rather than serializing it."""
    with pytest.raises(ExplorationRefusal):
        grouped([replace(row(0, 1, 1, 0), credits_earned_y1=float('inf'))])


def test_source_row_limit_uses_all_attempts_before_calculation(tmp_path, monkeypatch):
    """Refuse the entire step when source rows exceed the budget, even for one unit."""
    from analytics.exploration.datasets import build
    from analytics.tests.test_student_year1 import source
    from measures.requests import Filters
    from measures.tests.explorer_fixture import here, make_database, student

    path = make_database(tmp_path / 'data.db', [student('private')],
        [here('private', '2023-24', 'FALL', delivery='O') for _ in range(3)])
    snapshot = source(path)
    monkeypatch.setattr('analytics.exploration.datasets.MAX_SOURCE_ROWS', 2)
    try:
        with pytest.raises(ExplorationRefusal, match='limit_exceeded'):
            build(snapshot, '2023-24', Filters())
    finally:
        snapshot.named.close()
        snapshot.positional.close()


def test_catalog_metadata_is_executable_and_safe():
    """Catalog order/pairs/versions come from the same constants used by executors."""
    from analytics.exploration.catalog import metadata

    document = metadata()
    assert document['ordered_differences']['retention_outcome_school'] == [['not_retained', 'retained']]
    assert len(document['ordered_differences']['online_count_0_1to2_3plus']) == 3
    assert len(document['numeric_pairs']) == 5
    assert document['gateway_variant']['available'] is False
    assert json.loads(json.dumps(document)) == document
