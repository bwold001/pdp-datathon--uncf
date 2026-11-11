# Defined operation catalog and adapters

[Issue #49](https://github.com/bwold001/pdp-datathon--uncf/issues/49) adds the provider-free catalog and single-operation adapters used by the [v2 plan API](analysis-v2-api.md). All data/results are synthetic. Existing v1 URLs, formulas, response models and provider tools keep their behavior.

## Owners and calls

`measures/requests.py` owns pure cohort-bar validators and immutable dashboard parameter models. `api/filters.py` reuses these validators while retaining configured cohort choices, metadata and public names. V2 contracts import the same parameter types, keeping proposal, executable and catalog schemas together. Measures do not import API, analytics, FastAPI or provider code.

`measures/registry.py` registers eleven dashboard definitions with stable IDs/versions, labels/aliases, purpose, executable parameter schema, supported filters/grouping, grain/population/window, exclusions, coverage requirements, executor reference, units, component denominators, disclosure profile and limitations. `measures/service.py` validates and dispatches to existing measure/page owners on the supplied snapshot. It contains no metric formulas.

`analytics/legacy_operations.py` adds three defined legacy entries with original coverage requirements. `analytics/analysis_service.py` combines the catalog, searches compact descriptions, returns full details on demand, and converts owner results into typed v2 evidence. Gateway course outcomes also call `gap_finder.gateway.add_gateway_gaps`, exactly as the API does, without recreating comparisons.

```python
from analytics.analysis_service import AnalysisService

service = AnalysisService(coverage)
candidates = service.catalog("gateway success")
details = service.details("gateway.course_outcomes")
with legacy_service.snapshot() as snapshot:
    evidence = service.execute({
        "kind": "defined_measure", "step_id": "retention",
        "operation_id": "retention.rate",
        "parameters": {"cohort": "2023-24", "retention_type": "school"},
    }, snapshot)
```

`execute` borrows the snapshot without closing it. Invalid requests fail before reads; cancellation/database errors propagate to the outer owner. A course lacking disclosed evidence returns a legitimate unavailable result. `legacy_step(old_request)` maps a fully resolved old request; incomplete old requests still need the existing clarification flow.

This is **internal single-operation evidence**, not a complete plan executor or HTTP endpoint. Catalog/snapshot freshness, version resolution, dependency scheduling, exploration, plan-wide disclosure and final receipts remain later work. Do not serialize this evidence as a final chat response before those checks. Existing display suppression alone does not prevent inference by subtraction.

The [disclosure boundary](analysis-v2-disclosure.md) now supplies versioned profiles, a policy stamp on staged evidence, shared API execution and a conservative complete-plan projection primitive. The future plan executor must call that primitive on the actual returned set before constructing public receipts.

## Registered meanings

| ID | Existing meaning |
| --- | --- |
| `retention.rate` | Explicitly selected school/PDP or next-fall federal implementation; federal is not claimed fully IPEDS compliant. |
| `persistence.rate` | Other-college persistence flag. |
| `dfw.rate` | Classifiable final-grade enrollments; distinct students determine suppression. |
| `dfw.course_list`, `dfw.course_detail` | Course/term/delivery/group breakdowns with their own enrollment denominators. Detail requires a course. |
| `credit_completion.ratio` | Mean of individual student ratios, preserving its fractional numerator, never total earned divided by total attempted. |
| `credit_momentum.summary` | Milestones, tiers, term credits and Credit progress, with selected school/federal retention. |
| `gateway.math_completion`, `gateway.english_completion` | Requirement-based cohort completion at the existing 1.0-or-pass semantics. |
| `gateway.course_outcomes` | Year-one first-attempt 2.0-or-P outcomes, retakes, selected retention and gap-finder comparisons. |
| `student_paths.summary` | Term statuses, transitions, transfers and selected retention; two to six terms. |
| `legacy.graduation` | Credential/program-specific four-year, six-year and to-date perspectives, including unknown completion-program evidence. |
| `legacy.entry_major_retention` | Overall and entry-program retention with known outcomes. |
| `legacy.annual_enrollment` | Actual distinct enrollees in the latest two explicitly certified years, across entry cohorts. |

Scalars support the eight cohort-bar filters and up to two categorical grouping dimensions. Pages accept those filters; only Student paths permits request grouping, limited to one dimension. Course/term/delivery splits belong to DFW detail. Legacy entries reject dashboard filters and annual enrollment rejects a cohort override. Gateway aliases return distinct candidate meanings for clarification; no C-or-better cohort variant is enabled.

## Typed projection and limits

Rate payloads preserve owner numerator/denominator/rate, distinct students, exclusions, out-of-scope count and immutable D/F/W split. Optional bounded `breakdowns` retain each requested group's scope, status, inputs and exclusions. Hidden groups have only categorical scope/status/reason. Receipt validation checks grouping against the executed request. Provisional retention/persistence follows supplied coverage; absent cohort gateway reporting becomes `not_reported`, matching the API.

Aggregate pages use a typed long-form table: component path, numeric value, text value and counting unit. Order and all returned fields are preserved, with no recalculation or JSON blob cells. `courses[0].den` counts enrollments while `courses[0].students` counts students. Component denominator descriptions remain in catalog metadata/evidence context. Boolean context is text, never a count.

Explicit hidden nested components become hidden rows with no cells. A null leaf without an explicit owner status remains `unknown`; the adapter cannot invent whether missing evidence or suppression caused it. Top-level hidden evidence contains only status/reason. Visible legacy rows retain perspective, horizon, program/year/ethnicity scope, inputs, exclusions and notes. Hidden rows carry only status; coverage cutoff/years, program definition and attribution limitations remain in evidence context.

The existing v2 bound is 200 table rows. Oversized pages/analyses return typed `limit_exceeded` instead of truncating, recomputing or embedding extra JSON. Broad pages can exceed this bound: narrow filters, select DFW detail or reduce the Student paths horizon. Returning larger pages requires a future approved pagination/representation contract. No result cache is added.

## Verification and handoff

The independent twelve-student fixture has 24 final-grade enrollments, twelve D grades, six retained students and a credit-ratio numerator of 35/6. Tests cover all eleven dashboard operations, separate retention definitions, gateway reporting, hidden/provisional/grouped results and bounded projection. Three-student fixtures exercise all legacy operations and original coverage. Serialized v1 JSON/CSV are checked against the same explicit expectations, including Gateway's shared gap-finder projection.

Run registry, defined/legacy operation, rate-breakdown and API parity tests, then `make check-fast` and full `make check`. No browser/provider is needed for this inactive boundary. PostgreSQL parity still requires the configured integration environment from the [snapshot guide](analysis-v2-snapshots.md). Next planned work is [issue #50](https://github.com/bwold001/pdp-datathon--uncf/issues/50).

The complete-plan owner now calls this adapter through the [v2 API](analysis-v2-api.md), including whole-plan validation, source/version checks, disclosure and receipt construction. Existing provider tools are still unchanged. Current dashboard minimum-group configuration comes from merged `main`; legacy/exploration policies remain independent.
