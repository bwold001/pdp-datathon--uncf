# Student Success Chat v2 acceptance matrix

This is the current release acceptance specification for issue #53. Release A includes eleven defined operations and three distinct legacy adapters; registered deterministic exploration belongs to Release B. Requirements below are gates, not claims of passing behavior. All data and hand-counted examples are synthetic. The Task 0 inventory is historical; current registry, execution and result-policy implementations take precedence.

The [Task 0 inventory](chat-v2-baseline.md) records historical behavior; [ADR 0001](adr/0001-chat-v2-analysis-boundary.md) describes the shared boundary. Use the current test owners below for executable evidence and the [release handoff](release-a-handoff.md) for run results and unresolved gates.


### Routing and conversation cases

Use a scripted provider for deterministic state-machine tests. Keep a separate fixed prompt evaluation set for a real configured model; do not put network calls in ordinary CI. Provider tests prove orchestration, while the prompt evaluation measures the model's interpretation. Do not claim one proves the other.

Create at least thirty fixed prompts spanning the cases below, including paraphrases and combined filters. Store expected operation IDs, required constraints, and expected clarification fields, not expected model prose. Before enabling a release, all critical cases must avoid wrong numerical execution or dropped constraints. Record correct routing, necessary clarification, unnecessary clarification, and unsupported outcomes separately. Use the configured production model and record its ID; switching models requires rerunning this evaluation.

| Question or event | Required outcome |
| --- | --- |
| DFW rate for Pell students, with cohort | `dfw.rate`, `pell=Y`; complete scope confirmation. |
| Same question without cohort or client context | Clarify cohort; retain Pell. |
| Compare retention across existing credit tiers | `credit_momentum.summary`, existing boundaries, declared retention type. |
| Compare across user-defined tiers | Release A declines unsupported custom grouping; registered exploration belongs to Release B. |
| Retention next fall versus next academic year | Select distinct retention meanings; clarify if ambiguous. |
| Gateway success using C or better | Clarify cohort completion versus first-attempt course outcomes and `P` treatment. Cohort completion uses the existing >=1.0 or pass semantics; first-attempt year-one course outcomes use >=2.0 or P. Preserve each denominator and attempt rule; do not substitute one for the other. |
| Online course load related to credits earned | Release A refuses unsupported exploration before calculation; Release B resolves count/share and period. |
| Why are students leaving | Explain available observational evidence and ask for an observable comparison; no causal numerical answer. |
| Official retention, then characteristics of non-retained students | Two separately labeled steps with explicit populations and one snapshot. |
| Ask for a small Pell DFW group | Return every mathematically defined statistic with its sample size or denominator; never hide because the group is small. Unsupported exploration is still refused. |
| Provider omits Pell | No unconfirmed broader calculation; scope omission is visible and tested. |
| Incomplete proposal sent to execution | Reject before calculation; complete clarification and deterministic conversion first. |
| Independent second step fails in a usable transaction | Preserve first receipt, explicit partial outcome, continue only safe independent work. |
| Database timeout aborts shared transaction | Preserve completed aggregate receipts, mark remaining steps unexecuted, finish cleanup; no new snapshot. |
| Same input executed twice | Same computation fingerprint, distinct execution IDs; timestamps do not alter the fingerprint. |
| Replay needs an absent implementation/policy version | `version_unavailable`; no substitution. |
| Unsupported exploration explicitly requested through chat or direct API | Reject the whole plan before calculation; defined provider-free API remains available. |
| Provider returns a number with no execution | Numerical prose is not displayed as a result. |
| One of two steps needs clarification | Preserve both steps and all parameters. |
| Data/catalog changes after confirmation was prepared | Return stale-plan information and updated review scope. |
| User resets while request is running | Late response cannot repopulate the reset conversation. |
| New question during clarification | Start a new plan; discard old pending scope. |

### Independent numerical fixtures

Use deliberately small synthetic datasets. Every nonempty group stays visible, including sizes 1–9. Test old `UNCF_MIN_STUDENTS` and legacy `suppression_threshold` values of 10 and 100 to establish that they cannot restore hiding. There is no test-only threshold switch or production threshold-ten gate.

| Fixture | Expected property |
| --- | --- |
| One student has several final grades | DFW enrollment denominator differs from distinct student count. |
| Grades 0.69, 0.70, 1.99, 2.00, `P`, `W`, `I`, unknown | Existing boundaries and exclusion rules remain unchanged. |
| Student credit ratios 1/2 and 1 | Mean completion ratio is 0.75, not a ratio of combined credit totals. |
| Existing credit-tier boundaries | Credits below 15, from 15 to below 30, and at least 30 use the existing groups. |
| Student fails course, later passes it | First-try pass count remains zero; a passing retake within year one counts as an eventual pass. |
| Required student with no attempt | Cohort completion and course-taker populations remain distinct. |
| Student belongs to two cohorts | No join multiplication; correct cohort-specific online exposure. |
| Online values [0, 1, 2], credits [0, 2, 4] | Pearson coefficient is +1 in an arithmetic fixture. |
| Same online values, credits [4, 2, 0] | Pearson coefficient is −1. |
| Constant online exposure | Correlation unavailable because variance is zero. |
| Credits [10, missing, 30] | Complete-case mean is 20, with the missing case accounted for. |
| Groups of every size 1–9 | Dashboard JSON, CSV, final v2 receipts and chat cards retain defined values and their applicable n. |
| Small complements, exclusions, linked and overlapping groups | Keep all defined statistics, comparisons and rankings visible, including when overlap is uncertain; student rows and identifiers never serialize. |
| Zero numerator, positive denominator | Valid zero rate; an empty denominator does not produce a rate. |
| Missing evidence and invalid metadata | Preserve missing, unknown, unreported, unavailable and not-yet-observable states; never replace them with zero. Invalid counts, nonfinite values and inconsistent metadata fail validation. |
| One observed value | A mean is valid at n=1; Pearson needs at least two paired observations and nonzero variance. |
| Changed snapshot with same question | New fingerprint; stale replay does not silently use new data. |

Additional Release B fixtures must cover metric-specific n for earned/attempted means, unknown/unobservable retention exclusions, all three ordered online differences, mathematically unavailable difference inputs, and bounded occupied groups. Cross-step cases cover totals, partitions, linked exclusions, overlapping means/counts and uncertain relationship metadata without numerical withholding. Assert serialized payloads and application-generated text. Historical suppressed receipts remain historical; omitted values require recomputation under the current versioned policy. Do not claim minimum-size or repeated-query inference protection.

Do not force known inconsistent source fields to reconcile. If cohort credits and summed course credits differ, preserve the chosen source and report the distinction. A shared wrong answer can pass parity, so retain independent arithmetic fixtures alongside parity tests.

### Test file ownership

- `measures/tests/test_operation_registry.py`: defined capabilities and strict requests.
- `measures/tests/test_chat_v2_baseline.py`, `test_grades.py` and breakdown tests: independent formulas and boundaries.
- `analytics/tests/test_defined_operations.py`, `test_legacy_operations.py` and `test_analytics_calculations.py`: all fourteen adapters and distinct populations/horizons.
- `analytics/tests/test_contracts_v2.py`, `test_analysis_contracts.py`, `test_disclosure.py`: contracts, plans and mathematical visibility.
- `analytics/tests/test_snapshots.py`, `test_snapshots_postgres.py`, `test_provenance.py`: transactions, cleanup, identity and replay.
- `api/tests/test_analysis_v2.py`: provider-free HTTP, complete-plan validation and failures.
- `api/tests/test_defined_operation_parity.py`, `test_disclosure_parity.py`, `test_small_results.py`: dashboard/API/CSV parity and small groups.
- `playground/server_application/tests/test_chat_v2.py`: scripted provider, clarification, exact confirmation and same-snapshot dashboard/CSV/direct API/chat serialization.
- `playground/server_application/tests/test_release_a_evaluation.py`: fixed prompt inventory and scorer checks; live interpretation remains separate.
- `playground/client_application/src/components/uncf/chat/chat.stories.tsx`: cards, payload kinds, reset, stale responses and page navigation.
- Release B exploration fixtures remain future work; they are not Release A support claims.


## Independent fixture ledger and current evidence

Expected values below are written from the specified inputs, never generated by the function under test. Existing test fixtures remain authoritative for their current cases; v2 adapters preserve the same arithmetic and current versioned result policy.

| Case | Synthetic inputs and hand calculation | Current executable evidence / future owner |
| --- | --- | --- |
| Gateway definitions | Ten students recorded R/C receive 1.5 on their first math attempt; ten required R/D students have no attempt. Cohort completion is 10/20 = .5 under the >=1.0 requirement/completion semantics. Course outcomes have ten takers and zero C-or-better passes because 1.5 is below 2.0; P also passes. Non-attempters remain outside the course-taker denominator. | `measures/tests/test_chat_v2_baseline.py::test_gateway_cohort_completion_and_course_outcomes_have_different_populations`; `analytics/tests/test_defined_operations.py` verifies adapter behavior. |
| Fractional credit numerator | Nine students earn 1 of 2 credits and one earns 10 of 10: sum ratios = 5.5, denominator ten, rate .55. Combined credit ratio 19/28 is a different statistic. | `test_credit_completion_preserves_a_fractional_numerator` in the same baseline test file. |
| Tier retention denominator | Twelve students earn six credits; six retained, four not retained, two unknown. Tier size = 12 and share = 1; retention = 6/10 = .6. | `test_tier_size_is_not_the_known_retention_denominator`; `test_v2_credit_tiers_keep_known_retention_denominator` verifies the explicit known-outcome n. |
| DFW grain and small groups | Each student has one F and one P. Nine students yield 9/18 = .5 with distinct-student n nine; ten yield 10/20 = .5 with n ten. Enrollment denominator and student n stay separate and visible. | `measures/tests/test_chat_v2_baseline.py` and small-result serialization tests; no minimum-size hiding. |
| Existing school retention | `measures/tests/fixture.sql` has 16 retained of 20 known, four excluded: .8; persistence 5/20 = .25. | `measures/tests/test_measures.py::test_retention_for_everyone`, `test_persistence_for_everyone`. |
| Existing credit tiers and means | Ten students each earn 6/12, 24/24, 30/30; two have unknown credits. Means: attempted 22, earned 20 over 30 students. Milestones: 20,20,10 at 12,24,30. Completion = 25/30 = .8333. | `measures/tests/test_breakdown_credit_momentum.py::test_tiles_milestones_and_tiers`; means and completion have different eligibility. |
| Repeated gateway attempt | Ten students fail ENG 101 in fall and earn >=2.0 or P in the same course in spring; zero first-try passes, ten eventual passes, and ten in the retook-and-passed path. | `measures/tests/test_breakdown_gateway_courses.py::test_first_try_path_and_retention` covers ten such students alongside the other paths. |
| Legacy known retention | Retention answers [1,0,missing] give 1/2 = .5, one excluded; unknown program remains a category. | `analytics/tests/test_analytics_calculations.py::test_retention_keeps_known_outcomes_and_unknown_program`. |
| Legacy program overlap | One student has two courses in one program and one in another in the same year: each program gets count one, not three students. A no-course record is excluded. | `analytics/tests/test_analytics_calculations.py::test_enrollment_deduplicates_program_year_not_course_rows`. |
| Legacy graduation perspectives | Two selected-program entrants graduate, one switches out; one entrant from another program switches in. Any-program 2/2, selected-program 1/2, composition entered/switched-in each 1/2. Six-year horizon unobservable when only four certified. | `analytics/tests/test_analytics_calculations.py::test_graduation_perspectives_are_distinct_and_horizons_independent`; fixture-resolved completion programs do not imply the real extract has them. |
| Future correlations | x=[0,1,2], y=[0,2,4] gives +1; y=[4,2,0] gives -1; constant x has zero variance and no defined Pearson result. | Release B exploration arithmetic fixtures; no threshold-based withholding. |
| Future means/differences | Earned [10,missing,30] -> mean 20, n two; attempted [20,40,40] -> 100/3, n three. Group means [10,20,30] in online order [0,1–2,3+] give differences [+10,+20,+10] in declared comparison order. | Future exploration operation/request fixtures; no exploration executor exists yet. |

## Release evidence boundaries

Release A requires exactly `retention.rate`, `persistence.rate`, `dfw.rate`, `dfw.course_list`, `dfw.course_detail`, `credit_completion.ratio`, `credit_momentum.summary`, `gateway.math_completion`, `gateway.english_completion`, `gateway.course_outcomes`, `student_paths.summary`, `legacy.graduation`, `legacy.entry_major_retention` and `legacy.annual_enrollment`. Preserve registered versions, schemas, perspectives, horizons and coverage rules. No exploratory executor is exposed. No new feature flags, flag configuration, discovery, gates or flag-specific tests are required. Capability discovery reports implemented contracts and exact source-schema prerequisites; request-specific evidence and coverage are separate facts.

Release A requires the defined/legacy subset of this matrix, scripted provider/state tests, fixed production-model prompt evaluation, direct API/dashboard/CSV/chat evidence and deployment rollback documentation at issue #53. Record the actual checkout SHA. Compare source, build, pipeline, normalization, configuration and policy/version stamps on one known synthetic snapshot as well as independent expected numbers; matching source hashes alone do not establish equivalent normalization. Missing six-year follow-up must not disable valid four-year or observed-to-date evidence. School/federal retention remain distinct without a full IPEDS-compliance claim. Credit completion remains the mean of student ratios, including fractional numerators, rather than a ratio of pooled credit totals.

Run targeted root tests, `make check-fast`, `make check`, and the applicable Playground `mise run api:lint`, `api:test`, `web:lint`, `web:build` and `web:test-storybook` tasks using the declared toolchain. After merged PR #71, `api:test` builds disposable SQLite fixtures; no starter database, Docker or migrations are required for local checks. Run configured PostgreSQL integration before claiming that backend. Missing environments remain unverified and block release claims or deployments requiring them. Never reset a developer database for validation. Provider-key absence must produce a readable chat failure while deterministic endpoints stay provider-free. Check deadlines, cancellation/cleanup, independent bounded refusals, database interruption, partial outcomes and replay failures for missing versions/snapshots. Page payloads must render without silent omissions.

Record release and previous known-good revisions, environment/data compatibility, v1 compatibility checks and operator redeployment steps. Rollback uses the previous known-good deployment and requires no destructive data reset. Use an authorized local/preview environment for rehearsal, or record revision/compatibility checks when deployment access is unavailable. Do not claim an unperformed rehearsal. In-flight requests finish bounded cleanup without a protocol change mid-response. This issue authorizes no production deployment, merge or rollback.

Release B additionally requires correct dataset grain/missingness, precise per-statistic n and comparison order, bounds, whole-plan visibility, mixed execution/failures and replay at issue #57. Neither parity nor screenshots replace arithmetic tests. PostgreSQL, live-model and deployed-source checks must be reported separately when their environments exist.
