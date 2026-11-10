"""Real database to additive API tests, including disclosure and reload behavior."""
import sqlite3

import pytest

from fastapi.testclient import TestClient

from api.route import create_app
from analytics.service import AnalyticsService
from api.analyses import get_service
from analytics.tests.analytics_fixtures import build_database, fixture_coverage


def test_real_database_api_and_calculation_text_match(tmp_path):
    """The API returns actual counts and preserves existing route registration."""
    path = build_database(tmp_path / 'data.sqlite')
    service = AnalyticsService(path, fixture_coverage())
    app = create_app()
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as client:
        response = client.post('/api/v1/uncf/analyses', json={'analysis': 'retention', 'cohort': '2022-23'})
        assert response.status_code == 200
        receipt = response.json()['receipts'][0]
        row = receipt['rows'][0]
        assert (row['numerator'], row['denominator'], row['rate']) == (1, 2, .5)
        assert row['calculation'] == '1 / 2 = 50.00%'
        assert receipt['loaded_at'] == '2026-06-30T12:00:00'
        assert '/api/v1/uncf/results' in client.get('/openapi.json').json()['paths']
        assert client.post('/api/v1/uncf/analyses', json={'analysis': 'retention', 'sql': 'select *'}).status_code == 422
        assert client.post('/api/v1/uncf/analyses', json={'analysis': 'retention', 'cohort': '2099-00'}).status_code == 422
    old = receipt['source_stamp']
    with sqlite3.connect(path) as db:
        db.execute("UPDATE data_provider SET loaded_at='2026-07-01'")
    assert service.analyze({'analysis': 'retention', 'cohort': '2022-23'}).receipts[0].source_stamp != old


def test_suppression_hides_counts_and_substitutions(tmp_path):
    """Small cells cannot reappear in totals, exclusions or calculation text."""
    service = AnalyticsService(build_database(tmp_path / 'data.sqlite'), fixture_coverage(10))
    receipt = service.analyze({'analysis': 'retention', 'cohort': '2022-23'}).receipts[0]
    assert all(r.status not in ('ok', 'provisional') for r in receipt.rows)
    for row in receipt.rows:
        assert row.numerator is None and row.denominator is None
        assert not row.exclusions and not row.calculation


def test_clarification_and_all_graduation_horizons(tmp_path):
    """Ambiguities do not trigger a guess and degree timing stays honest."""
    service = AnalyticsService(build_database(tmp_path / 'data.sqlite'), fixture_coverage())
    request = {'analysis': 'graduation'}
    for field, value in [('cohort', '2022-23'), ('credential', 'B'), ('program', 'chemistry_general')]:
        response = service.analyze(request)
        assert response.clarification.field == field
        request = {**response.clarification.pending.model_dump(), field: value}
    receipt = service.analyze(request).receipts[0]
    assert len(receipt.rows) == 15
    assert receipt.rows[0].numerator == 1
    assert receipt.rows[0].denominator == 2
    assert receipt.rows[1].denominator == 1  # known non-completer; unresolved graduate excluded
    assert receipt.rows[5].status == 'not_yet_observable'
    assert receipt.rows[2].status == 'unknown'


def test_enrollment_uses_two_complete_years_and_cohort_join(tmp_path):
    """Duplicate courses and the student's other cohort do not multiply the count."""
    service = AnalyticsService(build_database(tmp_path / 'data.sqlite'), fixture_coverage())
    receipt = service.analyze({'analysis': 'enrollment'}).receipts[0]
    assert receipt.academic_years == ['2022-23', '2023-24']
    assert len(receipt.rows) == 3
    assert all(row.count == 1 for row in receipt.rows)
    assert all(row.denominator is None for row in receipt.rows)


def test_missing_database_and_uncertified_years_are_unavailable(tmp_path):
    """No data or uncertified completeness never becomes a numerical zero."""
    service = AnalyticsService(tmp_path / 'missing.sqlite', fixture_coverage())
    assert service.analyze({'analysis': 'enrollment'}).receipts[0].rows[0].status == 'unavailable'
    from analytics.coverage import Coverage
    service = AnalyticsService(build_database(tmp_path / 'data.sqlite'), Coverage())
    assert service.analyze({'analysis': 'enrollment'}).receipts[0].rows[0].status == 'unavailable'


def test_service_does_not_infer_bachelor_major_from_earliest_duration(tmp_path):
    """Earlier associate timing and a later course major never fabricate a bachelor semester."""
    path = build_database(tmp_path / 'data.sqlite')
    with sqlite3.connect(path) as db:
        db.execute('ALTER TABLE cohort_membership ADD COLUMN first_year_to_a_or_c_at_cohort INTEGER')
        db.execute("UPDATE cohort_membership SET first_year_to_a_or_c_at_cohort=1, time_to_credential=.8 WHERE student_id='a' AND cohort='2022-23'")
    service = AnalyticsService(path, fixture_coverage())
    receipt = service.analyze({'analysis': 'graduation', 'cohort': '2022-23',
                               'credential': 'B', 'program': 'chemistry_general'}).receipts[0]
    assert receipt.rows[0].numerator == 1
    assert receipt.rows[1].numerator == 0
    assert receipt.rows[1].exclusions['unknown_completion_program'] == 1
    assert receipt.rows[2].status == 'unknown'


def test_safe_retention_total_survives_fully_hidden_program_breakdown():
    """A safe overall rate can remain visible when every linked program count is hidden."""
    from analytics.presentation import rate_row, suppress
    rows = [rate_row('All majors', 50, 100),
            rate_row('Small program', 1, 2, group={'entry_program': '400501'}),
            rate_row('Other program', 49, 98, group={'entry_program': '520201'})]
    projected = suppress(rows, 10)
    assert projected[0].rate == .5
    assert projected[0].calculation == '50 / 100 = 50.00%'
    assert all(r.status == 'suppressed' for r in projected[1:])
    assert all(r.numerator is None and r.denominator is None and not r.calculation for r in projected[1:])


def test_calculation_text_uses_the_serialized_rate_rounding():
    """Calculation text and the UI's returned rate cannot disagree at rounding boundaries."""
    from analytics.presentation import rate_row
    row = rate_row('Rounding boundary', 10, 1600)
    assert row.rate == .0063
    assert row.calculation == '10 / 1600 = 0.63%'


@pytest.mark.parametrize('credential,first_field,latest_field', [
    ('A', 'first_year_to_associates_at_coho', 'years_to_latest_associates_at_co'),
    ('C', 'first_year_to_certificate_at_coh', 'years_to_latest_certificate_at_c'),
])
def test_associate_and_certificate_use_their_own_completion_evidence(tmp_path, credential, first_field, latest_field):
    """Two eligible entrants yield one credential-specific completion, independent of bachelor evidence."""
    path = build_database(tmp_path / 'data.sqlite')
    with sqlite3.connect(path) as db:
        db.execute(f'ALTER TABLE cohort_membership ADD COLUMN {first_field} INTEGER')
        db.execute(f'ALTER TABLE cohort_membership ADD COLUMN {latest_field} INTEGER')
        db.execute("UPDATE cohort_membership SET credential_type_sought_year_1=? WHERE cohort='2022-23'", (credential,))
        db.execute(f"UPDATE cohort_membership SET {first_field}=2, {latest_field}=2, first_year_to_bachelors_at_coh=0, years_to_ba_at_cohort_inst=0 WHERE student_id='a' AND cohort='2022-23'")
        db.execute(f"UPDATE cohort_membership SET {first_field}=0, {latest_field}=0 WHERE student_id='b' AND cohort='2022-23'")
    app = create_app()
    app.dependency_overrides[get_service] = lambda: AnalyticsService(path, fixture_coverage())
    with TestClient(app) as client:
        response = client.post('/api/v1/uncf/analyses', json={
            'analysis': 'graduation', 'cohort': '2022-23', 'credential': credential, 'program': 'chemistry_general'})
    assert response.status_code == 200
    receipt = response.json()['receipts'][0]
    assert (receipt['rows'][0]['numerator'], receipt['rows'][0]['denominator'], receipt['rows'][0]['rate']) == (1, 2, .5)
    assert receipt['rows'][0]['calculation'] == '1 / 2 = 50.00%'
    assert receipt['rows'][5]['status'] == 'not_yet_observable'
    assert receipt['rows'][1]['exclusions']['unknown_completion_program'] == 1


def test_standalone_analysis_errors_use_the_existing_error_envelope(tmp_path, monkeypatch):
    """Additive endpoints return useful errors to clients using the existing envelope."""
    service = AnalyticsService(build_database(tmp_path / 'data.sqlite'), fixture_coverage())
    app = create_app()
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as client:
        response = client.post('/api/v1/uncf/analyses', json={'analysis': 'retention', 'cohort': '2099-00'})
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_analysis'
    app.dependency_overrides.clear()
    bad_config = tmp_path / 'bad.yaml'
    bad_config.write_text('complete_academic_years: [')
    monkeypatch.setenv('UNCF_ANALYTICS_CONFIG', str(bad_config))
    with TestClient(app) as client:
        response = client.get('/api/v1/uncf/analyses/catalog')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'analytics_unavailable'


def test_native_timestamp_metadata_matches_text_metadata(tmp_path):
    """Driver-native dates retain the same receipt and provenance as SQLite text dates."""
    from contextlib import contextmanager
    from datetime import datetime

    path = build_database(tmp_path / 'dates.sqlite')
    request = {'analysis': 'retention', 'cohort': '2022-23'}
    expected = AnalyticsService(path, fixture_coverage()).analyze(request)
    sqlite3.register_converter('NATIVE_TIMESTAMP', lambda raw: datetime.fromisoformat(raw.decode()))
    with sqlite3.connect(path) as db:
        db.executescript('''
            ALTER TABLE data_provider RENAME TO old_provider;
            CREATE TABLE data_provider (provider_id INTEGER, loaded_at NATIVE_TIMESTAMP,
                                        source_file TEXT, file_sha256 TEXT);
            INSERT INTO data_provider SELECT * FROM old_provider;
            DROP TABLE old_provider;
        ''')

    @contextmanager
    def typed_connection():
        """A real DB-API connection returning native timestamps, as PostgreSQL does."""
        db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        try:
            yield db
        finally:
            db.close()

    actual = AnalyticsService(None, fixture_coverage(), connection_factory=typed_connection).analyze(request)
    assert actual == expected
