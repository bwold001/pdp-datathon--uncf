"""Actual HTTP mixed-plan evidence, failure and replay acceptance fixtures."""

import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from analytics.coverage import Coverage
from analytics.service import AnalyticsService
from analytics.tests.test_snapshots import add_identity
from api.analysis_v2 import get_runtime_factory
from api.route import create_app
from measures.tests.explorer_fixture import here, make_database, student

PREFIX = '/api/v1/uncf/analysis-v2'


def step(operation='grouped_summary', step_id='summary', **parameters):
    """Name only explicit registered scopes in a synthetic exploration request."""
    defaults = {'grouping': 'online_count_0_1to2_3plus'} if operation != 'correlation' else {'x': 'online_enrollment_count_y1', 'y': 'credits_earned_y1'}
    return {'kind': 'exploratory_analysis', 'operation': operation, 'dataset_id': 'student_year1', 'step_id': step_id,
        'parameters': {'cohort': '2023-24', **defaults, **parameters}}


@pytest.fixture
def browser(tmp_path):
    """Six units with independent credits, two valid online comparisons and one exclusion."""
    values = [(10,20,0,1), (None,40,0,0), (30,40,0,0), (15,25,1,0), (5,10,3,0), (99,99,None,None)]
    students, records = [], []
    for i, (earned, attempted, online, retained) in enumerate(values):
        students.append(student(f'private-{i}', earned=earned, attempted=attempted, retention=retained))
        records.extend(here(f'private-{i}', '2023-24', 'FALL', delivery='F' if online == 0 else 'O' if online else None)
            for _ in range(max(1, online or 0)))
    path = make_database(tmp_path / 'data.db', students, records)
    add_identity(path)
    app = create_app()
    app.dependency_overrides[get_runtime_factory] = lambda: lambda: AnalyticsService(path, Coverage(suppression_threshold=100))
    with TestClient(app) as client:
        yield client, path


def plan(client, *steps):
    """Use real application catalog/snapshot references for every execution."""
    catalog = client.get(PREFIX + '/catalog').json()
    return {'kind': 'executable', 'catalog_version': catalog['catalog_version'], 'snapshot_ref': catalog['snapshot_ref'], 'steps': list(steps)}


def test_mixed_four_method_plan_json_and_replay(browser):
    """One snapshot returns independent arithmetic and exact deterministic replay identities."""
    client, _ = browser
    retention = {'kind': 'defined_measure', 'operation_id': 'retention.rate', 'step_id': 'retention',
        'parameters': {'cohort': '2023-24', 'retention_type': 'school'}}
    raw = plan(client, retention, step(), step('mean_comparison', 'comparison'), step('correlation', 'relationship'))
    body = client.post(PREFIX + '/execute', json=raw).json()
    assert body['outcome'] == 'complete', body
    receipts = body['receipts']
    assert receipts[0]['result']['payload']['value'] == .2
    assert receipts[1]['result']['payload']['rows'][0]['cells'] == ['zero', 3, 20, 2, 1, 100/3, 3, 0]
    assert [d['value'] for d in receipts[2]['result']['payload']['differences']] == [-5, -15, -10]
    assert receipts[3]['result']['payload']['n'] == 4
    # Hand arithmetic: pairs (0,10),(0,30),(1,15),(3,5): covariance sum=-30;
    # squared deviations are 6 and 350, so r=-30/sqrt(2100).
    assert receipts[3]['result']['payload']['coefficient'] == pytest.approx(-30 / (2100 ** .5))
    assert len({r['source']['snapshot_ref'] for r in receipts}) == 1
    assert {m['id'] for m in receipts[1]['versions']['methods']} == {'grouped_summary','mean_comparison','pearson'}
    assert 'private-' not in json.dumps(body) and 'student_id' not in json.dumps(body)
    replay = client.post(PREFIX + '/execute', json=body['replay']).json()
    assert replay['outcome'] == 'complete'
    assert [r['computation_fingerprint'] for r in replay['receipts']] == [r['computation_fingerprint'] for r in receipts]
    assert [r['result'] for r in replay['receipts']] == [r['result'] for r in receipts]
    assert replay['execution']['execution_id'] != body['execution']['execution_id']


def test_safe_refusal_partial_and_database_failure_stop(browser, monkeypatch):
    """Independent evidence survives safe refusals; poisoned connections stop further work."""
    from analytics.exploration import operations
    from analytics.exploration.datasets import ExplorationRefusal

    client, _ = browser
    original = operations.execute
    calls = []

    def fail(operation, parameters, snapshot):
        """Refuse one step without poisoning its borrowed transaction."""
        calls.append(operation)
        if operation == 'mean_comparison':
            raise ExplorationRefusal('limit_exceeded')
        return original(operation, parameters, snapshot)

    monkeypatch.setattr(operations, 'execute', fail)
    raw = plan(client, step(), step('mean_comparison', 'refused'), step('correlation', 'independent'))
    body = client.post(PREFIX + '/execute', json=raw).json()
    assert body['outcome'] == 'partial'
    assert [r['step_id'] for r in body['receipts']] == ['summary', 'independent']
    assert calls == ['grouped_summary', 'mean_comparison', 'correlation']

    def interrupted(operation, parameters, snapshot):
        """Trigger a real driver failure after a completed sibling."""
        if operation == 'mean_comparison':
            snapshot.named.execute('SELECT missing_private_column FROM term')
        return original(operation, parameters, snapshot)

    monkeypatch.setattr(operations, 'execute', interrupted)
    body = client.post(PREFIX + '/execute', json=raw).json()
    assert body['outcome'] == 'partial'
    assert [r['step_id'] for r in body['receipts']] == ['summary']
    assert body['step_outcomes'][-1]['outcome'] == 'not_executed'
    assert 'missing_private_column' not in json.dumps(body)


def test_unavailable_dependency_and_missing_versions(browser):
    """Unavailability completes honestly; dependencies cannot use nonexistent evidence."""
    client, _ = browser
    variant = {'kind':'exploratory_analysis','operation':'measure_variant','dataset_id':'student_year1','step_id':'variant',
        'parameters':{'cohort':'2023-24','variant_id':'gateway.cohort_completion_c_or_better'}}
    dependent = {**step(), 'depends_on':['variant']}
    body = client.post(PREFIX + '/execute', json=plan(client, variant, dependent)).json()
    assert body['outcome'] == 'partial'
    assert body['receipts'][0]['result']['reason'] == 'unsupported_evidence'
    assert body['step_outcomes'][1]['issue']['code'] == 'dependency_unavailable'
    body = client.post(PREFIX + '/execute', json=plan(client, step())).json()
    body['replay']['versions']['methods'][0]['version'] = 'missing'
    failed = client.post(PREFIX + '/execute', json=body['replay']).json()
    assert failed['issues'][0]['code'] == 'version_unavailable' and not failed['receipts']


@pytest.mark.parametrize('n', range(1, 10))
@pytest.mark.parametrize('threshold', ['10', '100'])
def test_sparse_http_results_preserve_exact_n(tmp_path, monkeypatch, n, threshold):
    """Actual endpoint JSON keeps n=1 through n=9 and a single missing-exposure exclusion."""
    monkeypatch.setenv('UNCF_MIN_STUDENTS', threshold)
    path = make_database(tmp_path / 'sparse.db',
        [student(f'private-{i}', earned=10, attempted=20, retention=0) for i in range(n + 1)],
        [here(f'private-{i}', '2023-24', 'FALL', delivery='F') for i in range(n)])
    add_identity(path)
    app = create_app()
    app.dependency_overrides[get_runtime_factory] = lambda: lambda: AnalyticsService(path, Coverage(suppression_threshold=int(threshold)))
    with TestClient(app) as client:
        body = client.post(PREFIX + '/execute', json=plan(client, step())).json()
        assert body['outcome'] == 'complete'
        result = body['receipts'][0]['result']
        assert result['payload']['rows'][0]['cells'] == ['zero', n, 10, n, 0, 20, n, 0]
        assert result['exclusions'] == [{'reason':'no_year1_records','count':1}]
        assert 'private-' not in json.dumps(body)
