# Student Success Chat v2 acceptance matrix

This matrix is the Task 0 acceptance specification for issue #46, recorded before v2 implementation. It incorporates the required checks from the revised plan. A requirement here is not a claim of passing v2 behavior. All data and hand-counted examples are synthetic.

Current executor ownership and existing behavior are in [the baseline inventory](chat-v2-baseline.md); the intended shared boundary is in [ADR 0001](adr/0001-chat-v2-analysis-boundary.md). V2 contract/registry/exploration test files named below are future owners. Existing checks and the five new baseline cases are identified separately at the end.


### Routing and conversation cases

Use a scripted provider for deterministic state-machine tests. Keep a separate fixed prompt evaluation set for a real configured model; do not put network calls in ordinary CI. Provider tests prove orchestration, while the prompt evaluation measures the model's interpretation. Do not claim one proves the other.

Create at least thirty fixed prompts spanning the cases below, including paraphrases and combined filters. Store expected operation IDs, required constraints, and expected clarification fields, not expected model prose. Before enabling a release, all critical cases must avoid wrong numerical execution, dropped constraints, and suppression bypasses. Record correct routing, necessary clarification, unnecessary clarification, and unsupported outcomes separately. Use the configured production model and record its ID; switching models requires rerunning this evaluation.

| Question or event | Required outcome |
| --- | --- |
| DFW rate for Pell students, with cohort | `dfw.rate`, `pell=Y`; complete scope confirmation. |
| Same question without cohort or client context | Clarify cohort; retain Pell. |
| Compare retention across existing credit tiers | `credit_momentum.summary`, existing boundaries, declared retention type. |
| Compare across user-defined tiers | Registered exploratory grouping if supported; otherwise clarify or decline that grouping. |
| Retention next fall versus next academic year | Select distinct retention meanings; clarify if ambiguous. |
| Gateway success using C or better | Resolve cohort-completion versus course-taker population and `P` treatment. Both current gateway operations pass at >=1.0 or P; C-or-better requires a registered variant with grade evidence. |
| Online course load related to credits earned | Exploratory request; resolve count/share and period when needed. |
| Why are students leaving | Explain available observational evidence and ask for an observable comparison; no causal numerical answer. |
| Official retention, then characteristics of non-retained students | Two separately labeled steps with explicit populations and one snapshot. |
| Give suppressed Pell DFW using another calculation | No exploratory bypass. |
| Provider omits Pell | No unconfirmed broader calculation; scope omission is visible and tested. |
| Incomplete proposal sent to execution | Reject before calculation; complete clarification and deterministic conversion first. |
| Independent second step fails in a usable transaction | Preserve first receipt, explicit partial outcome, continue only safe independent work. |
| Database timeout aborts shared transaction | Preserve safely disclosed completed receipts, mark remaining steps unexecuted, finish cleanup; no new snapshot. |
| Same input executed twice | Same computation fingerprint, distinct execution IDs; timestamps do not alter the fingerprint. |
| Replay needs an absent implementation/policy version | `version_unavailable`; no substitution. |
| Exploration disabled but explicitly requested through direct API | Reject without calculation; defined provider-free API remains available. |
| Provider returns a number with no execution | Numerical prose is not displayed as a result. |
| One of two steps needs clarification | Preserve both steps and all parameters. |
| Data/catalog changes after confirmation was prepared | Return stale-plan information and updated review scope. |
| User resets while request is running | Late response cannot repopulate the reset conversation. |
| New question during clarification | Start a new plan; discard old pending scope. |

### Independent numerical fixtures

Use deliberately small synthetic datasets. Tests may set the disclosure threshold to one through a trusted fixture configuration for arithmetic checks; keep separate production-threshold tests at ten.

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
| Nine students versus ten students | Correct threshold boundary; no suppressed numeric inputs leak. |
| Visible total plus hidden partition | Exploration disclosure prevents recovery of the hidden partition. |
| Changed snapshot with same question | New fingerprint; stale replay does not silently use new data. |

Additional Release B fixtures must cover metric-specific n for earned/attempted means, unknown/unobservable retention exclusions, all three ordered online differences, hidden difference inputs, and twenty versus twenty-one occupied groups including hidden groups. Add cross-step disclosure cases covering an aggregate, a hidden partition, linked exclusions, an overlapping exploratory mean/count, and uncertain relationship metadata. Assert safe serialized payloads and application-generated text, not only internal suppression flags.

Do not force known inconsistent source fields to reconcile. If cohort credits and summed course credits differ, preserve the chosen source and report the distinction. A shared wrong answer can pass parity, so retain independent arithmetic fixtures alongside parity tests.

### Test file ownership

- `measures/tests/test_registry.py`: operation capabilities and request validation.
- `measures/tests/test_service.py`: adapters, unit preservation, and existing formulas.
- `analytics/tests/test_contracts_v2.py`: result and plan validation.
- `analytics/tests/test_disclosure.py`: profiles and hidden evidence.
- `analytics/tests/test_snapshots.py`: identity, consistency, cancellation, and ownership.
- `analytics/tests/test_exploration_datasets.py`: grain, joins, and missingness.
- `analytics/tests/test_exploration_operations.py`: independent calculations and limits.
- `analytics/tests/test_analysis_plans.py`: complete-plan validation and mixed execution.
- `api/tests/test_analysis_v2.py`: provider-free HTTP behavior and legacy compatibility.
- Extend `api/tests/test_consistency.py`: dashboard/API/chat service equivalence.
- Playground tests: scripted-provider routing, clarification, confirmation, tool limits, and deployment wiring.
- Client stories/tests: result payload kinds, full plan state, reset, and stale responses.

Names are proposed. Reuse existing fixtures and consolidate with an existing test file when that makes ownership clearer.


## Independent fixture ledger and current evidence

Expected values below are written from the specified inputs, never generated by the function under test. Existing test fixtures remain authoritative for their current cases; future v2 adapters must preserve the same arithmetic without inheriting inappropriate disclosure profiles.

| Case | Synthetic inputs and hand calculation | Current executable evidence / future owner |
| --- | --- | --- |
| Gateway definitions | Ten students recorded R/C receive 1.5 on their first math attempt; ten required R/D students have no attempt. Cohort completion is 10/20 = .5. The gateway course has ten takers, ten first-try passes and ten eventual passes because 1.5 meets the >=1.0 gateway threshold; all other path counts are zero. | `measures/tests/test_chat_v2_baseline.py::test_gateway_cohort_completion_and_course_outcomes_have_different_populations`; registry/service adapter tests follow. |
| Fractional credit numerator | Nine students earn 1 of 2 credits and one earns 10 of 10: sum ratios = 5.5, denominator ten, rate .55. Combined credit ratio 19/28 is a different statistic. | `test_credit_completion_preserves_a_fractional_numerator` in the same baseline test file. |
| Tier retention denominator | Twelve students earn six credits; six retained, four not retained, two unknown. Tier size = 12 and share = 1; retention = 6/10 = .6. | `test_tier_size_is_not_the_known_retention_denominator`; future v2 typed table must explicitly carry known n. |
| DFW threshold and grain | Each student has one F and one P. Nine students yield 18 classifiable enrollment rows but suppress all scalar evidence. Ten yield 10/20 = .5, distinct-student n ten. | Two parameterized cases in `test_dfw_threshold_counts_students_instead_of_enrollments`; threshold is production ten. |
| Existing school retention | `measures/tests/fixture.sql` has 16 retained of 20 known, four excluded: .8; persistence 5/20 = .25. | `measures/tests/test_measures.py::test_retention_for_everyone`, `test_persistence_for_everyone`. |
| Existing credit tiers and means | Ten students each earn 6/12, 24/24, 30/30; two have unknown credits. Means: attempted 22, earned 20 over 30 students. Milestones: 20,20,10 at 12,24,30. Completion = 25/30 = .8333. | `measures/tests/test_breakdown_credit_momentum.py::test_tiles_milestones_and_tiers`; means and completion have different eligibility. |
| Repeated gateway attempt | Ten students fail ENG 101 in fall and pass the same course in spring; zero first-try passes, ten eventual passes, and ten in the retook-and-passed path. | `measures/tests/test_breakdown_gateway_courses.py::test_first_try_path_and_retention` covers ten such students alongside the other paths. |
| Legacy known retention | Retention answers [1,0,missing] give 1/2 = .5, one excluded; unknown program remains a category. | `analytics/tests/test_analytics_calculations.py::test_retention_keeps_known_outcomes_and_unknown_program`. |
| Legacy program overlap | One student has two courses in one program and one in another in the same year: each program gets count one, not three students. A no-course record is excluded. | `analytics/tests/test_analytics_calculations.py::test_enrollment_deduplicates_program_year_not_course_rows`. |
| Legacy graduation perspectives | Two selected-program entrants graduate, one switches out; one entrant from another program switches in. Any-program 2/2, selected-program 1/2, composition entered/switched-in each 1/2. Six-year horizon unobservable when only four certified. | `analytics/tests/test_analytics_calculations.py::test_graduation_perspectives_are_distinct_and_horizons_independent`; fixture-resolved completion programs do not imply the real extract has them. |
| Future correlations | x=[0,1,2], y=[0,2,4] gives +1; y=[4,2,0] gives -1; constant x has zero variance and no defined Pearson result. | Future exploration-operation arithmetic fixtures with trusted threshold one, plus separate threshold-ten cases. |
| Future means/differences | Earned [10,missing,30] -> mean 20, n two; attempted [20,40,40] -> 100/3, n three. Group means [10,20,30] in online order [0,1–2,3+] give differences [+10,+20,+10] in declared comparison order. | Future exploration operation/request fixtures; no exploration executor exists yet. |

## Release evidence boundaries

Release A requires the defined/legacy subset of this matrix, scripted provider/state tests, fixed production-model prompt evaluation, direct API/dashboard/CSV/chat evidence, flags and rollback at issue #53. Exploration must remain disabled.

Release B additionally requires correct dataset grain/missingness, the precise per-statistic n and comparison order, bounds, whole-plan disclosure and uncertain-overlap refusal, mixed execution/failures, and replay at issue #57. Neither parity nor screenshots replace arithmetic tests. PostgreSQL, live-model and deployed-source checks must be reported separately when their environments exist.
