# Versioned disclosure and API parity

[Issue #50](https://github.com/bwold001/pdp-datathon--uncf/issues/50) centralizes existing display rules and adds a conservative disclosure boundary for a future complete v2 plan. All fixtures/results are synthetic. Existing dashboard numerical policy is preserved; this migration does not repair its documented cross-result subtraction issue.

## Owners and profiles

`measures/disclosure.py` contains the dependency-free policy definitions and predicates. Measures/models cannot import analytics orchestration without creating a cycle, so `analytics/disclosure.py` builds legacy projection and plan-level exploration handling on those definitions. Each registered profile has version `1` and a default minimum of ten:

| Application-selected profile | Behavior |
| --- | --- |
| `dashboard_v1` | Existing per-owner dashboard rules: scalar suppression counts distinct students, page components keep their existing populations/rules, zero page counts remain visible, and gateway missing reporting remains `not_reported`. A small numerator/complement alone does not newly suppress a dashboard rate. |
| `legacy_analytics_v1` | Existing legacy small count/numerator/denominator/complement/exclusion checks, linked-family suppression, and safe overall-total exception. The trusted coverage configuration retains its existing threshold setting; fixture threshold one is not a request parameter. |
| `exploration_v1` | At least ten distinct analysis units; safe binary complements, exclusion counts and comparison inputs; conservative whole-family and mixed-plan withholding. No model-selected policy/threshold is accepted. |

Legacy projection has one implementation, `suppress_legacy`; `analytics/presentation.py` retains compatible helper exports. Legacy service execution applies that policy once. The former inactive registry label `legacy_v1` is corrected to the canonical `legacy_analytics_v1`; the legacy behavior is unchanged. Catalog metadata is now `defined-2` and includes policy version, population/grain, partitions, measures and the possibility of overlap between scopes. Different operation IDs/cohort labels do not prove disjoint populations.

The dashboard runner's threshold and component predicates now come from the versioned profile. Measures/page owners still perform their existing disclosure at calculation time; adapters never rerun dashboard output through legacy suppression. `OperationEvidence` carries the registry-selected policy ID/version. `stage_defined(step_id, spec, evidence)` checks that stamp and operation version, then stages the already-disclosed result without applying another policy.

## Dashboard/API/CSV execution

Dashboard page routes and both `/measures/{measure}` and legacy `/results` dispatch through `measures.service.execute` on a caller-owned read transaction. Load timestamps are read from that transaction. Existing API response shapes/statuses, metadata, query defaults, formulas and caches remain supported. JSON and CSV consume the same cached disclosed result objects.

One export defect was found by the new acceptance tests: DFW detail stores `groups` as dimension-keyed lists, while the previous CSV loop treated it as a flat list and crashed. Export now flattens each existing group record with its dimension. Other page list exports retain their existing layout. No counts or suppression rules change for this correction.

Independent fixture checks prove that a dashboard result with one retained student out of twelve remains visible in JSON, CSV and a serialized v2 receipt, even though the legacy policy would suppress that numerator. Existing tests continue covering fractional credit completion, DFW enrollments versus distinct students, page denominators, hidden groups, exclusions, provisional status and gateway nonreporting. No v2 HTTP route is enabled here.

## Complete-plan protection boundary

`disclose_plan(staged, relations)` accepts one to four unique internal `StagedEvidence` records and returns only typed `DisclosedStep` projections. Inputs contain trusted executor facts: distinct-unit count, binary/exclusion counts, group unit counts and optional linked partition-family identity. These facts and `DisclosureRelation` records must come from registry/executor code, never provider/client parameters. This module does not derive exact overlap proofs from natural language or arbitrary query strings.

For exploration, means/correlations must match the declared distinct sample; counts/rates check small complements, and comparisons require visible input-group sample sizes. Tables require group unit counts for every row and conservative checks of integer cells. Missing sample/group evidence fails closed. Existing unavailable/unknown/unobservable result statuses are preserved without inventing numbers.

Unsafe linked families withhold exploratory totals, differences, exclusions and other payload cells. A hidden defined input can also protect an exploratory sibling in that family even when the category populations are disjoint. Defined dashboard output is preserved. Every exploratory step with another plan step is withheld unless a trusted registry relation establishes disjointness; recognized overlap, partition relationships and unknown/missing relationships all withhold its numerical evidence. The policy deliberately does not infer safe compatibility for overlapping exploratory queries. Even with disjointness, local/family checks still run.

Withheld results contain only a hidden status/reason. The returned `comparisons_allowed` flag is false for withheld evidence or results with hidden inputs; callers must omit derived ranks and narrative comparisons. The projector returns no staged raw counts, relationship metadata or free-text conclusions. Subsequent receipt assembly must use this projected result and application-controlled metadata, not copy numerical prose from an internal calculation or provider response.

The actual plan executor and exploratory registry remain later work. They must stage the whole actual returned set after transaction cleanup, supply trustworthy unit/family/relationship facts, call this boundary once before serialization, and bind policy/context versions into the fingerprint and receipt. An operation-local call alone does not establish complete-plan safety. A partial plan must project its actual surviving set, rather than assuming a planned but failed step was returned.

This boundary does not change defined-only dashboard subtraction behavior, account across requests/conversation history, or protect unlimited repeated queries over real student data. Broader dashboard complementary suppression requires a coordinated policy/version and dashboard/API/CSV expectation change. Production disclosure accounting is separate scope.

## Validation and next task

Tests cover existing dashboard and legacy behavior, policy binding, hidden input preservation, each supported statistic shape, small binary/exclusion cells, linked partitions, mixed-plan recognized/unknown overlap, proven disjointness, malformed relationships, and JSON/CSV/final-receipt boundaries. API dispatch spies verify every page and both scalar URLs use the shared service once, including reuse for export.

Run focused disclosure/API tests, then `make check-fast` and full `make check`. PostgreSQL and live-provider verification remain environment-dependent; SQLite tests do not establish backend parity. No client/Playground source changes are required. Next planned work is [issue #51](https://github.com/bwold001/pdp-datathon--uncf/issues/51).
