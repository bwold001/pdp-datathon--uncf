# Analysis v2 contracts

`analytics/contracts_v2.py` defines the version 2 wire boundary for [issue #47](https://github.com/bwold001/pdp-datathon--uncf/issues/47). Existing `analytics/schemas.py`, v1 endpoints, provider tools and client transports remain unchanged. These types do not enable an operation, authorize database access, compute a statistic or claim a disclosure policy was applied. All example evidence is synthetic.

## Requests and confirmation

`ExecutablePlan` requires `kind: executable`, a catalog version, snapshot reference and one to four typed steps. Each step has a unique ID and up to three dependencies. Dependencies must name earlier steps, so unknown references, self-dependencies, forward references and cycles fail before execution. Object properties not in the schema are forbidden throughout the boundary.

Steps discriminate first by `kind`, then by operation selector. Defined and legacy requests use `operation_id`; exploratory requests use `operation` plus `dataset_id: student_year1`. The eleven defined schemas preserve operation-specific capabilities: scalar grouping is limited to two distinct cohort-bar dimensions; course detail requires a course; page summaries reject arbitrary grouping; retention definitions are explicit; student paths supports two to six terms and at most one grouping. Three legacy adapters retain their own parameter domains. Correlation accepts only its numeric features, Pearson and complete cases, without a grouping field. Grouped operations require a registered grouping. Variants accept only a named variant, with no formula or threshold override.

These schemas describe the planned protocol vocabulary, not current catalog availability. The later registry/service must validate current cohorts, available operations, approved feature pairs, source coverage and policy versions. For example, accepting the gateway variant's request shape does not establish the normalized evidence required to execute it. The new credit-progress section and Gateway student-path redesign on current `main` must remain part of their later page adapters; neither requires an additional request parameter here. Preserve component-specific denominators and reuse `gap_finder/gateway.py` for the Gateway comparisons rather than recreating them in chat.

`ProposedPlan` uses `kind: proposed`. It keeps the same operation-specific shape, but a permitted material parameter can instead contain an explicit choice:

```json
{
  "unresolved": true,
  "question": "Which cohort?",
  "choices": [
    {"value": "2022-23", "label": "2022-23"},
    {"value": "2023-24", "label": "2023-24"}
  ]
}
```

Choice options must satisfy that parameter's executable field type. Missing required fields or null placeholders do not stand in for unresolved choices. Filters/grouping lists retain their concrete types. Proposal models are derived from executable field definitions once at module import so their field constraints do not drift; they never inherit an executable step's type. The generated classes have distinct names and JSON Schema references for each operation.

`resolve_choice(plan, step_id, parameter, value)` accepts a current option on a whitelisted parameter key, never an arbitrary dotted path. It returns a newly validated plan while preserving every other step. `to_executable(plan)` refuses unresolved choices and deterministically converts the complete proposal, including defaults. Confirmation presents this exact executable scope. Later execution adapters must revalidate it against current catalog/source references; structural validation alone cannot detect stale external state.

All records are frozen and nested collections are tuples or frozen typed models. `canonical_json` sorts object keys, includes resolved defaults, and refuses nonfinite numbers. Set-like grouping/dependency fields are canonicalized; step, table-row and comparison order remain meaningful and are preserved. Explicit boundary revalidation also checks model instances, since Pydantic's construction/copy escape hatches are not validation APIs.

## Evidence and hidden results

A `Receipt` binds an executed step to operation/version, canonical request, population/window/grain, definition references, assumptions/limitations/baseline changes, synthetic source identity, coverage, computation versions, fingerprint and execution timestamps. Receipt IDs must match their requests and execution completion cannot precede its start. The response additionally checks the request, snapshot and catalog against the confirmed plan.

Visible results use `ok` or `provisional`, a discriminated payload and bounded disclosed exclusions:

- Counts require a nonnegative integer and a meaningful counting unit.
- Rates allow fractional numerators and require positive denominators, declared units and agreement with division at the declared precision.
- Means accept finite values outside 0–1 and an eligible sample size.
- Mean comparisons carry visible group means/sample sizes and explicit ordered subtraction pairs. Group means retain the precision of the calculation inputs; each returned difference must equal their subtraction rounded to its declared precision. The renderer must not calculate the difference again. Registered grouping order and which comparisons to execute remain operation-owner rules.
- Pearson results require paired sample size of at least two, coefficient within −1 to 1, and x/y units. Visible correlation receipts also require versions for the selected features and Pearson method. Zero variance is represented as unavailable evidence by the future executor.
- Tables have at most 32 uniquely named, typed columns and 200 rows, with units per column. Each visible row has exactly the declared number and types of cells; booleans are not counts. A hidden row has a status and no cells. Tables are the bounded representation for multi-component page and legacy results, not an arbitrary JSON extension point.

Top-level hidden results discriminate `suppressed`, `unknown`, `unavailable`, `not_yet_observable` and `not_reported`. They carry only a fixed reason code: numerical payloads, exclusions and calculation text are forbidden. Payload kind must agree with the requested operation, so a valid mean cannot masquerade as a DFW rate. User IDs, arbitrary raw rows, connection strings and implementation paths have no receipt fields; `student_id` is also rejected as a table column.

These checks do not implement suppression accounting or prove that every free-text label/metadata string is safe. Registry-controlled columns, application-generated metadata, and final plan-wide disclosure projection are still required before serialization. Do not copy provider prose, database errors or intermediate rows into result messages. Source fingerprints and version references are required evidence fields here; their construction, verification and replay behavior are documented in the [snapshot guide](analysis-v2-snapshots.md).

## Response states and failures

`AnalysisResponseV2` always uses `protocol_version: 2`. Before execution, `outcome` is null and receipts/step outcomes are empty. Clarification requires a whole proposed plan and a reference matching one current question/choice set. Confirmation requires an executable plan. Pre-execution errors require typed issues. Unsupported requests can have no plan when no supported operation exists.

After execution, ordered step outcomes must cover every step, and receipts must cover exactly the completed ones. A legitimate unavailable/suppressed receipt counts as completed execution, not a failed calculation. A dependent step without a completed usable parent receipt must instead be `not_executed` with `dependency_unavailable`.

The aggregate outcome is `complete` when all steps have receipts, `partial` when some completed and others failed/did not run, or `failed` when none completed. Responses with completed receipts use `answer`; an execution without any uses `error`. Uncompleted steps require a typed issue bound to their own ID. Runtime transaction cleanup, stop/continue rules and cancellation remain the later orchestration service's responsibilities; these schemas check the response's truthfulness, not the database state.

## Client fixtures and checks

`analytics/tests/fixtures/contracts_v2.json` contains hand-written protocol examples for confirmation, multi-step clarification, fractional credit completion, negative correlation, hidden evidence, partial and failed execution, a table with a hidden row, and pre-execution errors. No provider or database is involved. The tests deserialize/serialize the fixtures and inspect JSON Schema restrictions; a future TypeScript client can consume the same file.

Run `python -m pytest analytics/tests/test_contracts_v2.py -q`, then the root measures/analytics/API suite and `make check-fast`. Run `make check` before PR submission. Existing v1 tests also run to establish that introducing these types does not alter the old integer receipt contract. Next work is [issue #48](https://github.com/bwold001/pdp-datathon--uncf/issues/48): shared snapshots and reproducible identity, followed by registry/executor adapters; no provider integration is required yet.

Defined dashboard parameter models now live in `measures/requests.py` and are re-exported here. The [defined operation guide](analysis-v2-defined-operations.md) documents the shared catalog/adapters and optional typed rate breakdowns, distinct-student counts and immutable DFW split added for lossless owner conversion. Hidden breakdowns have no numerical fields; receipt validation binds group dimensions to the request.

The [deterministic v2 API](analysis-v2-api.md) now validates and executes these plans. Runtime path discrimination remains strict; JSON Schema retains nested operation unions while removing the invalid inline-object discriminator mapping that OpenAPI requires to be string references. New receipts name their disclosure profile, and replay exports include policy references.
