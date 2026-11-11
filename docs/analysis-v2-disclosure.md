# Versioned visibility and API parity

[Issue #50](https://github.com/bwold001/pdp-datathon--uncf/issues/50) centralizes result visibility and shared execution. All fixtures/results are synthetic. Every nonempty group is eligible for display, including groups of one. There is no minimum-size, numerator, complement, exclusion, linked-family or overlap suppression rule.

## Owners and profiles

`measures/disclosure.py` contains dependency-free profile definitions. `analytics/disclosure.py` validates staged evidence and projects complete plan results. Each registered profile now has version `2` and minimum sample `1`:

| Application-selected profile | Behavior |
| --- | --- |
| `dashboard_v1` | Every nonempty scalar population and page group is visible. Known zero counts remain visible; empty populations have no rate. Gateway missing reporting remains `not_reported`. |
| `legacy_analytics_v1` | Small counts, numerators, denominators, complements and exclusions remain visible, together with linked totals and groups. |
| `exploration_v1` | Valid nonempty samples and comparison inputs remain visible, including small cells and linked or overlapping scopes. |

Profile IDs remain stable for compatibility; their version changes identify the new behavior. Catalog `defined-3` advertises version `2`, population/grain, minimum sample, partitions, measures and possible overlap. `UNCF_MIN_STUDENTS` and legacy `suppression_threshold` settings cannot reenable hiding. The old `has_small_cell` and `suppress_legacy` helper exports remain callable as no-ops for compatibility; service execution no longer applies legacy suppression.

`OperationEvidence` carries the registry-selected policy ID/version. `stage_defined(step_id, spec, evidence)` validates that stamp and the operation version without reapplying a visibility policy. Evidence stamped with an earlier policy version must be recomputed before staging under version `2`. Previously stored receipts remain historical artifacts; removing suppression cannot reconstruct values omitted from them.

## Dashboard/API/CSV execution

Dashboard page routes and both `/measures/{measure}` and legacy `/results` dispatch through `measures.service.execute` on a caller-owned read transaction. Load timestamps come from that transaction. Existing API response shapes, formulas, query defaults and caches remain supported. JSON and CSV consume the same cached result objects.

DFW detail stores `groups` as dimension-keyed lists. Its exporter flattens those existing records with a `dimension` column rather than treating the dictionary as a flat list. Other page list exports retain their layout.

Groups of one through nine, fractional credit numerators, DFW enrollment counts and one-of-twelve rates remain visible through JSON, CSV and v2 evidence. Missing values, unknown outcomes, incomplete coverage, provisional states and gateway nonreporting retain their existing meaning. Empty populations have no rate. The historical `suppressed` status remains in response contracts for compatibility and empty-population results; it no longer means a nonempty group failed a size threshold. No v2 HTTP route is enabled here.

## Complete-plan projection

`disclose_plan(staged, relations)` accepts one to four unique internal `StagedEvidence` records and returns typed `DisclosedStep` projections. Executor facts and `DisclosureRelation` records remain application-owned, not model/client parameters. Unknown, overlapping, partitioned and linked populations are all permitted; relationships do not withhold numerical results.

Exploration validation still rejects inconsistent evidence: missing or nonpositive distinct-unit counts, negative count metadata, binary counts that do not partition the declared population, inconsistent mean/correlation sample sizes, counts above the population, rate denominator mismatches, and tables without input-group evidence for every row. These are validation errors, not suppression results. Valid one-unit inputs and zero complements are permitted.

Existing unavailable, unknown and unobservable results remain hidden because their values are not known. Historical hidden results are preserved without inventing payloads. `comparisons_allowed` is false for a result with hidden inputs; a hidden sibling does not suppress otherwise valid evidence. The projection contains no staged metadata or generated numerical narrative.

The actual plan executor and exploratory registry remain later work. They must stage the actual returned response set after transaction cleanup, validate evidence, and bind policy/context versions into receipts and fingerprints. No new exploration endpoint is enabled by this change.

## Impact and validation

Small groups can now appear in rankings and comparisons. Their rates can change sharply with a single student. Removing linked and overlap suppression also permits subtraction across related aggregates. This policy provides no minimum-size privacy protection or protection against inference from repeated queries if real student data is used. It changes visibility, not metric formulas, populations or denominators.

Tests cover groups of one through nine, small complements/exclusions, linked totals, recognized/unknown overlap, disjoint results, malformed metadata, policy-version binding, missing evidence, and JSON/CSV/final-receipt parity. Route spies verify shared service execution and cache reuse for export. Run `make check-fast` and full `make check`; PostgreSQL and live-provider checks remain environment-dependent.

Next planned work is [issue #51](https://github.com/bwold001/pdp-datathon--uncf/issues/51).
