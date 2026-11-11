# Deterministic analysis v2 API

[Issue #51](https://github.com/bwold001/pdp-datathon--uncf/issues/51) exposes the existing defined dashboard and legacy analyses without a model provider. All data/results are synthetic. Existing `/analyses`, dashboard and CSV contracts remain supported. Exploratory request shapes exist in the protocol, but exploratory operations are not registered for execution in this increment.

## Routes and source selection

| Route under `/api/v1/uncf/analysis-v2` | Behavior |
| --- | --- |
| `GET /catalog` | Current catalog/snapshot references, safe source/pipeline/build stamps, coverage declarations, bounded choices, schemas, aliases, executor references and exact missing schema prerequisites. |
| `POST /validate` | A whole `ProposedPlan` or `ExecutablePlan`; returns server-authored clarification, canonical confirmation or typed issues. No operation calculation runs. |
| `POST /execute` | An explicit `ExecutablePlan`, or an exported `ReplaySpec` containing one. Revalidates the entire plan before calculation, then returns disclosed receipts and truthful execution outcomes. |

Standalone uses the configured normalized extract and shared coverage configuration from the existing analytics service. Playground overrides the v2 runtime factory with its configured SQLite/PostgreSQL provider. The deterministic routes are mounted even when chat is disabled and do not require OpenRouter/provider credentials. They never fall back from Playground's selected source to the standalone file.

V2 requires the genuine build manifest introduced by the snapshot loader work. An old extract without supported build identity returns `version_unavailable`; v1 reads remain compatible. Rebuild through the complete documented loader pipeline rather than inventing a manifest or silently loading another source.

Catalog `available` means the source schema supports that executor, not that every cohort/filter/horizon has observable numerical evidence. Actual receipts retain unavailable/suppressed/nonreported outcomes. Certified complete years, cohort follow-up, cutoff and provisional declarations are exposed separately. Course choices are capped at 100 with `more_courses` explicit; a known course can still lack disclosed evidence for the requested filters. The existing 200-row result bound is unchanged.

## Explicit scope and clarification

Read catalog references before constructing a plan:

```json
{
  "kind": "executable",
  "catalog_version": "catalog-version-from-GET",
  "snapshot_ref": "snapshot-reference-from-GET",
  "steps": [{
    "kind": "defined_measure", "step_id": "retention",
    "operation_id": "retention.rate",
    "parameters": {
      "cohort": "2023-24", "retention_type": "school",
      "filters": {"pell": "Y"}, "group_by": []
    }
  }]
}
```

`/validate` materializes defaults and preserves all steps, including other unresolved choices. For a proposed field marked `unresolved`, the server replaces question/option labels with its current canonical choices and returns one allowed parameter reference. Resubmit the full proposed plan with the selected concrete value; arbitrary dotted-path updates are not accepted. `/execute` refuses a proposed plan, unresolved values, invalid arguments, unsupported operations, oversized plans and invalid dependency ordering/cycles before any calculation.

This direct API is stateless: the exact explicit submitted plan is the request. It does not store a chat confirmation session or infer meaning from a natural-language question. The later chat interaction must compare confirmation state and display inherited constraints explicitly. Validation cannot prove that a provider understood every word of an earlier question.

## Execution, failures and disclosure

`analytics/plan_service.py` coordinates the existing operation owners. All steps run sequentially on one worker and one read-only snapshot; there is no cross-thread connection sharing or student-level handoff. A concurrent atomic reload cannot mix generations within a plan. Source/load time and build identity come from that same snapshot.

The whole plan's IDs, concrete parameters, source/catalog references and schema capabilities are checked before the first calculation. A normal hidden or unavailable receipt is completed execution. A dependent step without usable parent evidence is `not_executed` with `dependency_unavailable`; it cannot substitute another population. A declared bounded application refusal can fail one step while independent work continues. A database error, connection failure or query/overall deadline stops remaining work without retrying or reopening a snapshot.

Rollback/close finish before any response. Completed evidence is retained for a partial response. If cleanup itself fails, all completed in-memory evidence is retained and the response includes a typed application-level issue. When every step has a receipt the outcome remains `complete`; the message explicitly reports the cleanup failure. Query cancellation uses the existing cooperative worker interruption; request cancellation also waits for worker cleanup. The server-only budget `UNCF_ANALYSIS_V2_TIMEOUT_SECONDS` defaults to 10 seconds and must be finite, positive and no greater than 60. Cleanup and bounded in-memory finalization can finish after the query deadline so a worker is never abandoned.

The complete actual returned set passes through the shared disclosure boundary after cleanup and before receipt serialization. Defined/legacy evidence retains its registry-selected version 2 policy: every nonempty small group, numerator, complement and exclusion remains visible, including linked and overlapping results. Missing evidence and empty denominators retain their existing statuses. No exploratory operation is enabled.

Responses use the shared v2 fields: `status`, `plan`, `outcome`, ordered `step_outcomes`, receipts, typed issues and application-authored message. Pre-execution errors have null outcome and empty receipts. Completed hidden receipts count toward `complete`; some completed evidence plus failure/skips is `partial`; no completed receipts is `failed`. Receipts use `answer` status; no completed evidence uses `error`. Successful/partial evidence returns HTTP 200, structural/capability errors 422, stale/unavailable references or versions 409, unavailable data 503 and deadline failure without receipts 504. Error bodies do not echo raw SQL, driver/configuration errors, secrets or internal paths.

## Versions and replay

Catalog versions include actual executable implementation, coverage/configuration, schema capabilities and registered operation versions. Requests with changed catalog references must be reviewed again; a replaced generation returns `snapshot_unavailable` rather than rerunning on new data. The catalog exposes safe normalization/pipeline/load-generation stamps for future API/chat preview comparison.

Each execution exports a `ReplaySpec`, fingerprint schema version `2`, all operation/policy references, implementation/configuration/coverage versions, canonical plan and normalization digest. Computation fingerprints exclude execution IDs/timestamps/durations and include ordered plan/dependencies without execution outcomes or obsolete suppression context. Separate execution stamps identify this run. Receipts name their selected disclosure profile/version explicitly. Replay revalidates the identified source and exact current versions; missing versions are not substituted, and inconsistent fingerprints are rejected. There is no historical data/code archive or result cache.

All three profiles retain their stable IDs (`dashboard_v1`, `legacy_analytics_v1`, `exploration_v1`) at version `2`, with minimum sample one and catalog `defined-3`. `UNCF_MIN_STUDENTS` and legacy suppression thresholds cannot hide nonempty groups. The active policy versions and coverage are included in configuration/fingerprints; obsolete dashboard environment settings and legacy `suppression_threshold` values do not change catalog or replay identity. Schema-1 replay and removed context fields are rejected before calculation rather than silently upgraded.

## Validation and handoff

HTTP tests use independently specified synthetic counts and real SQLite transactions. They cover metadata-only validation, clarification, full-plan refusal, JSON/OpenAPI restrictions, provider-free execution, replay/version refusal, hidden dependencies, partial/failed results, real query deadlines, database poisoning, cleanup order/failure, reload consistency, policy consistency and invalid input without secret echoing. Playground tests prove its configured source is used with chat disabled. PostgreSQL metadata/full-plan integration runs only when the existing PostgreSQL test environment is configured; a skipped environment does not establish parity.

Run focused endpoint/contracts/provenance/disclosure/setting tests, root `make check-fast` and full `make check`, plus Playground API lint/format and SQLite tests. This branch's client code comes from the already-merged `main` updates; client lint/build/Storybook are regression checks, not new v2 UI implementation. No production deployment or live-provider evaluation is part of this task. Next work is [issue #52](https://github.com/bwold001/pdp-datathon--uncf/issues/52).
