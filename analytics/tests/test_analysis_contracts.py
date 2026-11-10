"""Public input and program-evidence contracts."""
import pytest
from pydantic import ValidationError

from analytics.schemas import AnalysisRequest
from analytics.coverage import Coverage
from analytics.programs import final_program, normalize_program, resolve_program


def test_program_codes_are_not_guessed():
    """Only unambiguous six-digit codes are accepted."""
    assert normalize_program('40.0501') == '400501'
    assert normalize_program('090702') == '090702'
    assert normalize_program('90702') is None
    assert normalize_program('24.01') is None
    assert resolve_program('chemistry_general') == {'400501'}
    with pytest.raises(ValueError):
        resolve_program('chemical engineering')


def test_analysis_rejects_sql_and_incompatible_parameters():
    """Approved analyses accept only their typed parameters."""
    with pytest.raises(ValidationError):
        AnalysisRequest(analysis='retention', cohort='2022-23', sql='SELECT *')
    with pytest.raises(ValidationError):
        AnalysisRequest(analysis='enrollment', cohort='2022-23')


def test_rounded_duration_does_not_establish_an_award_semester():
    """A final major requires a resolved relevant semester."""
    terms = [{'term_id': 1, 'sort_order': 2, 'academic_year': '2022-23',
              'academic_term': 'SPRING', 'term_program_of_study': '400501'}]
    assert final_program(terms, None) is None
    assert final_program(terms, 1) == '400501'
    assert final_program(terms + [dict(terms[0], term_program_of_study='520201')], 1) is None
    assert final_program([dict(terms[0], academic_term='UNKNOWN')], 1) is None


def test_coverage_requires_declared_complete_years():
    """A stray future course row cannot certify completeness."""
    coverage = Coverage(complete_academic_years=['2022-23', '2023-24'],
                        provenance='Hand-counted synthetic fixture')
    assert coverage.latest_two_years() == ['2022-23', '2023-24']
    assert not coverage.observable('2022-23', 6)
    assert Coverage().latest_two_years() == []


@pytest.mark.parametrize('values', [
    {'numerator': 2, 'denominator': 4, 'rate': .999},
    {'numerator': -1, 'denominator': 4, 'rate': 0},
    {'numerator': 5, 'denominator': 4, 'rate': 1},
    {'numerator': 0, 'denominator': 0, 'rate': 0},
])
def test_receipts_reject_inconsistent_numbers(values):
    """A valid-looking receipt cannot carry a rate unrelated to its actual counts."""
    from analytics.schemas import CalculationRow
    with pytest.raises(ValidationError):
        CalculationRow(label='invalid', kind='rate', status='ok', **values)


def test_calculation_text_is_owned_by_the_contract():
    """Consumers cannot inject invented numerical explanations or hidden values."""
    from analytics.schemas import CalculationRow
    row = CalculationRow(label='retention', kind='rate', status='ok',
                         numerator=1, denominator=2, rate=.5, calculation='99.9%')
    assert row.calculation == '1 / 2 = 50.00%'
    with pytest.raises(ValidationError):
        CalculationRow(label='hidden', kind='rate', status='suppressed', calculation='1 / 2')
