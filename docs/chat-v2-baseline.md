# Student Success Chat v2 baseline and capability inventory

This is the Task 0 handoff for [issue #46](https://github.com/bwold001/pdp-datathon--uncf/issues/46), under [tracking issue #45](https://github.com/bwold001/pdp-datathon--uncf/issues/45). It records existing behavior before v2 contracts or dispatch are introduced. All fixtures and source data are synthetic; none of these values are findings about real students or institutions.

## Checkout and scope

- Inspected November 10, 2026, at `8407844177c87326b98dcd642c57c04eeece1a5b` (current `main` when fetched).
- Planning baseline: `c571f8b87a2d1ed93a8288d28e47aecf3e32d8d8`.
- Local implementation branch: `issue-46-chat-v2-baseline`; the isolated checkout started clean. Existing checkouts and their branches were not modified.
- Task 0 changes only documentation and hand-counted characterization tests. V2 IDs below are proposed stable names, not currently exposed API operations.
- Decisions: [ADR 0001](adr/0001-chat-v2-analysis-boundary.md). Required routing, arithmetic and release behavior: [acceptance matrix](chat-v2-acceptance.md).

### Changes since the planning baseline

`git diff --stat c571f8b87a2d1ed93a8288d28e47aecf3e32d8d8 HEAD` reports 20 changed files, 127 insertions and 102 deletions, before Task 0 edits. The merge of PR #44 introduced `/api/v1/uncf/measures/{measure}` and renamed `api/results.py` to `api/measure_by_group.py`; the hidden-schema `/results` compatibility route remains. `GroupRow`/response names and route tests changed accordingly. Use `api/tests/test_measure_by_group.py`, not the former `test_results.py`.

The same diff touches filter comments, definitions, DFW/student-path documentation, a gateway test assertion comment, client path/key-term text, deployment/analytics docs, README, AGENTS.md and dependency comments. The changed calculation-related files contain terminology updates rather than new formulas. No v2 implementation was present in this checkout. Do not apply the plan's old module names mechanically.

## Existing request capabilities

The HTTP cohort bar in `api/filters.py:CohortQuery` accepts `cohort_term`, `enrollment_intensity`, `enrollment_type`, `pell`, `gender`, `race`, `ethnicity`, and `age_band`. Cohorts currently offered are 2021-22 through 2024-25; default is 2023-24. `retention_type` is `school` (default) or `federal`. Input values must match the allowed list; SQL matching subsequently normalizes case/spaces and maps unlisted data values to UNKNOWN.

`api/schemas.py` limits public measure grouping to two distinct cohort-bar dimensions. The lower-level measures engine also supports `first_gen`, and DFW supports open `course`, `term`, and `delivery` dimensions. Those capabilities are not automatically public API filters/groupings. Page helpers select eight student dimensions. Registry contracts must advertise their actual adapter capabilities, not the union of every lower-level feature.

The scalar measure API exposes retention, persistence, gateway math/English, DFW and credit completion. Federal retention is selected through `retention_type` for the public retention operation. JSON and CSV share the same calculated rows. `api/route.py:run_page` dispatches the page helpers and adds context; it does not define their formulas.

## Defined operation inventory

All scalar executors below are called through `measures/run_measures.py:run_measure`, with cohort objects, validated filters, and optional grouping. Their rates are rounded to four places. For student measures the grain is student/cohort; a DFW record is an enrollment. Scalar disclosure uses distinct students with usable answers, not the number of selected or enrolled rows. A cohort with no usable in-scope answers yields `not_yet_observable`; a small group in an otherwise observable cohort is `suppressed`.

| Proposed v2 ID | Current executor | Population, numerator and denominator | Parameters, coverage and exclusions |
| --- | --- | --- | --- |
| `retention.rate` | `measures/calculations/retention.py:count` or `federal_retention.py:count` | School: true PDP retention flags / known flags. Federal: students with an actual course next fall / in-scope students once that fall appears in the course file. | Cohort, eight public filters, supported public groupings, explicit retention type. School unknown flags excluded. Federal currently includes all enrollment types and does not count credentials; observation is based on any course-file row in next fall, not certified completeness. |
| `persistence.rate` | `measures/calculations/persistence.py:count` | True PDP persistence flags / known flags; another institution's enrollment or credential by year two. | Cohort, filters, scalar grouping. Unknown outcome excluded. Public API marks configured recent cohort provisional independently of raw result status. |
| `dfw.rate` | `measures/calculations/dfw.py:count` | D/F/W course enrollments / enrollments with classifiable final grades, across course rows belonging to the entry cohort; not restricted to year one. | Cohort, supported filters/groupings. Numeric grades below .7 are F, .7 to below 2 are D; P passes; W and F count. Incomplete/audit/missing/other/unknown/unlisted excluded by reason. Suppression uses distinct students among counted grades. |
| `dfw.course_list` | `measures/breakdowns/dfw_courses.py:dfw_courses` | The same DFW overall/course enrollment counts; course metadata comes from final-grade rows. | Cohort and filters; fixed course breakdown, sorted by DFW count then rate. Hidden courses omitted and counted. No arbitrary grouping/time override. |
| `dfw.course_detail` | `measures/breakdowns/dfw_courses.py:dfw_course` | One normalized course code; fixed term, delivery and student-group enrollment counts, D/F/W splits and comparisons with the remaining course enrollments. | Required course, cohort, filters. Hidden/absent course raises `UnknownCourse` (HTTP 404). Rest-rate guard currently uses enrollment denominator; see D3 below. |
| `credit_completion.ratio` | `measures/calculations/credit_completion.py:count` | Sum of per-student earned/attempted ratios / eligible students; numerator may be fractional, not earned credits. Individual ratios capped at one. | Cohort, filters, scalar grouping. First-time/transfer-in, at least one attempted credit and known full/part-time required. Re-admit/continuing out of scope; unknown type/credits/attendance and attempted below one excluded. |
| `credit_momentum.summary` | `measures/breakdowns/credit_momentum.py:credit_momentum` | Cohort-credit means use students with both year-one credits known; completion reuses its measure eligibility; retention uses known answers; milestones use known-credit students; term means use students with course records that term. | Cohort, filters, retention type; fixed milestones 12/24/30; earned tiers [0,15), [15,30), [30,infinity). Both selected and known-credit groups must reach ten. A page has several distinct denominators. |
| `gateway.math_completion` | `measures/calculations/gateway_math.py:count` via `students.py:gateway_rows_sql` | Completed `C` / classified `C` or `D` outcomes among rows not marked not-required. C describes >=1.0 or pass in year one. Required non-attempters recorded D count in denominator. | Cohort, filters, scalar grouping. N requirement out of scope; missing/unclassified completion excluded. Unknown requirement with known completion is a documentation mismatch (D1). API maps no-answer gateway status to `not_reported`. |
| `gateway.english_completion` | `measures/calculations/gateway_english.py:count` via `students.py:gateway_rows_sql` | Same cohort completion algorithm as math, using the English fields. | Same supported scope and caveats as math; no course-taker denominator substitution. |
| `gateway.course_outcomes` | `measures/breakdowns/gateway_courses.py:gateway_courses`, `course_outcomes`, `course_pairs` | First attempt per course/student within cohort academic year; pass >=2.0 or P. Shares use classifiable first attempts; retention-by-outcome uses known retention answers. Pair denominator is known retention among joint first-term takers. | Cohort, filters, retention type. Whole-cohort gateway M/E flag presence controls classification; absent flags trigger declared college-level prefix inference. Nonfinal first attempts excluded, not replaced by later passing attempts. Pairs use all first-term course pairs, not only gateway courses; top three below cohort retention. |
| `student_paths.summary` | `measures/breakdowns/student_paths.py:student_paths` | Path shares use selected students with known entry terms. Retention separately uses all selected students with known answers, including unplaced students. Transfer counts use final displayed position. | Cohort, filters, retention type, 2–6 terms (default 3), optional one supported student dimension. Unknown start term excluded from path; absent observed term becomes `not_observed`, not a known stop-out. Cell counts 1–9 hidden; zeros can remain visible. |

These are existing page-specific implementations. Do not apply the stronger legacy chat projection to them to make new chat cards look uniform.

## Existing analysis inventory

The proposed distinct legacy adapter IDs below are documentation names pending registry implementation. Their existing transport remains `AnalysisRequest.analysis` with `graduation`, `retention`, or `enrollment`, dispatched by `analytics/service.py:AnalyticsService.analyze`.

| Proposed adapter ID | Executor and current request | Evidence, eligibility and limitations |
| --- | --- | --- |
| `legacy.graduation` | `analytics/graduation.py:calculate`; cohort, credential B/A/C, registered program required. | Student/cohort and selected credential. Four-year, six-year, to-date perspectives remain distinct. Any-program rate uses selected entry-program entrants with known timing; program-specific rate also needs known completion program for qualifying completions. Composition denominator is inferred selected-program graduates, not entrants. Service currently sets completion program unknown because exact award-semester evidence is absent. Rounded earliest credential time cannot infer it. |
| `legacy.entry_major_retention` | `analytics/retention.py:calculate`; cohort required, no Pell/other dashboard filters and no federal selector. | Overall and first-term-program retained / known school-retention outcomes; unknown program kept separately and unknown outcomes excluded. Preserves program partitions, recent-cohort provisional state and legacy suppression even though overall school-retention arithmetic agrees with the measure. |
| `legacy.annual_enrollment` | `analytics/enrollment.py:calculate` with `AnalyticsService.enrollments`; no entry-cohort parameter. | Distinct student per year/program/ethnicity among actual course enrollments in latest two certified complete academic years. Composite student/cohort join avoids multiplication; repeat courses deduplicate, changing program may count in both programs. Unknown ethnicity/program remain categories. Count payload has no rate denominator. |

`analytics/config/analytics.yaml` currently certifies no complete academic years, no cohort follow-up, and no cutoff. Default graduation horizons/annual enrollment can therefore be honestly unavailable/not-yet-observable, not demo-ready numerical capabilities. Tests explicitly declare synthetic coverage and must not confer that coverage on the shared extract. Program aliases/attribution live in `analytics/programs.py`.

## Existing disclosure, data and conversation seams

- Scalar dashboard projection: `run_measures.build_result`/`hidden_result`, threshold ten counted students; hidden rows remove values, exclusions and splits. The public gateway adapter remaps no-answer status to `not_reported`. API provisional metadata and legacy provisional row statuses are different contracts.
- Page projection: `breakdowns/common.py:shown` leaves zero visible, hides positive counts 1–9; `retained_share` requires ten known answers but can return smaller retained counts. Page-specific fields can therefore differ from scalar and legacy rules.
- Legacy projection: `analytics/presentation.py:suppress` checks positive small counts, numerators, denominators, complements and exclusions; hides linked visible rows, sometimes preserving one independently safe overall retention total. Cross-request privacy accounting is absent. See the existing complementary-disclosure limitation in `docs/solutions/best-practices/2026-11-01-compare-a-group-with-everyone-else.md`.
- `run_measure`/`read_answers` accept caller connections and do not close those; their SQL readers require `cursor()` and positional row behavior. Path wrappers open SQLite themselves. Page helpers open/close named-row SQLite and can separately reopen retention/measure connections.
- `AnalyticsService.connect` owns a read-only SQLite transaction with cancellation hooks, or uses the configured connection factory. Catalog/clarification and each `analyze` may open separate transactions. Confirming several legacy requests does not establish a shared plan snapshot.
- Playground `app/services/analytics.py:database` provides read-only repeatable-read PostgreSQL with dict rows and statement timeout, or read-only transactional SQLite with cancellation. Its `QueryConnection` supplies `execute` only; it does not yet satisfy measure cursor/positional-reader needs. It honors configured source rather than silently falling back.
- API cache identity is currently file modification time; legacy `source_stamp` hashes provider manifest rows including load time/provider IDs. Neither is the proposed versioned computation fingerprint. Loader `src/loader/backends.py:refresh` already changes normalized tables and load stamps within one transaction. Build on that boundary; an atomic file-replacement redesign is not automatically required.
- Existing model tools only read metadata and propose one of three analyses; confirmation executes deterministic calculations without another provider call. Six provider rounds, six tools per round, max 36 confirmed requests, and a 75-second route deadline are v1 limits. New four-step v2 limit must be separate.
- Current state keeps one unresolved analysis plus completed proposals; a second unresolved analysis is disclosed as needing a separate question. It does not preserve an arbitrary multi-unresolved-step plan. Client revision/reset ignores stale responses. Provider numerical prose never supplies result values.
- MCP currently registers metadata tools only; dormant general query support remains out of scope.

## Discrepancies and decisions for later implementation

| ID | Evidence and effect | Required treatment |
| --- | --- | --- |
| D1 | `students.py:gateway_rows_sql` documentation says unknown requirement is excluded, but SQL only treats N as out of scope and then accepts C/D regardless of R/UNKNOWN/null requirement. | Record actual behavior; preserve it during parity migration. Any stricter requirement eligibility is a separately approved definition/policy change. Do not represent the documentation as an implemented guard. |
| D2 | `credit_momentum.py:tiers` returns total tier membership as `students`, but `retained_share` calculates rate only over known outcomes and its known sample size is not included in that tier row. Twelve members, ten known, six retained yields .6, not .5. | V2 evidence needs an explicit known-outcome denominator obtained from shared helpers; never derive it from rounded rate. Preserve the v1 shape and avoid changing its numbers. |
| D3 | `dfw_courses.py:compare` guards rest size with course enrollment denominator minus group enrollment denominator, despite a student-based threshold elsewhere. | Preserve current dashboard behavior for parity and disclose the unit. Improving distinct-student complementary suppression is a coordinated policy change, not Task 0 refactoring. |
| D4 | Gateway page `course_pairs` builds first-term pairs from all course rows, not only rows classified as gateway. | Catalog wording must state this scope. Do not relabel it gateway-only or rebuild it as exploratory equity-gap search. |
| D5 | Plan names `api/results.py`, while current checkout uses `api/measure_by_group.py` and preserves the old URL. | Update implementation paths; preserve both deployed routes. |

## Baseline checks and next task

Environment: a fresh `.venv` using Python 3.14.10, with the checkout's exact `requirements.txt` installed. The host's default Python 3.9.6 does not satisfy the repository requirement and was not used for tests.

Before edits, `.venv/bin/python -m pytest measures/tests analytics/tests api/tests -m 'not slow' -q` completed with **206 passed, 6 skipped, 22 deselected**. The six skips are PostgreSQL cases without `PDP_TEST_POSTGRES_URL`.

Before edits, `make check-fast` completed successfully with the venv on PATH: manifest checks and all 52 documented quality counts matched; normalized model **402 passed / 5 skipped**, MCP **84 / 40**, measures **122 / 6**, gap finder **83 / 0**, analytics **27 / 0**, API **57 / 0**. Total **775 passed / 51 skipped**. There were no observed failing tests. Skips are not evidence of PostgreSQL support.

Task 0 adds five passing cases in `measures/tests/test_chat_v2_baseline.py`: distinct gateway populations/thresholds, a fractional credit numerator, tier retention's known-answer denominator, and DFW's nine/ten-student boundary despite two enrollment rows per student. Expected values are hand-counted, not generated by executors.

After changes, the same targeted command completed with **211 passed, 6 skipped, 22 deselected**. Final `make check-fast` passed with **780 passed / 51 skipped**: normalized model 402/5, MCP 84/40, measures 127/6, gap finder 83/0, analytics 27/0, API 57/0. Manifest and 52 quality-count checks also passed. `git diff --check` and local documentation-link/code-fence checks passed. No production calculation or response contract changed.

Before PR submission, full `make check` also passed: **787 passed / 74 skipped** (normalized model 408/6, MCP 84/40, measures 127/16, gap finder 84/0, analytics 27/0, API 57/12). Slow checks requiring an unavailable loaded extract or PostgreSQL remained skipped. These counts do not establish backend, browser or provider parity beyond the exercised environments.

Playground application tests, browser stories, live provider evaluation, PostgreSQL integration and deployment behavior are not validated by these root checks. No Playground implementation files changed. These remain explicit later release gates, not existing failures.

Next: [issue #47](https://github.com/bwold001/pdp-datathon--uncf/issues/47), strict `ProposedPlan`/`ExecutablePlan`, typed results, dependencies and outcomes. Read this baseline and the acceptance matrix, then add contract tests in `analytics/tests/test_contracts_v2.py` before `analytics/contracts_v2.py`. Do not start with provider integration.
