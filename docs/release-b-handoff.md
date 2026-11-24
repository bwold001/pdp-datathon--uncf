# Release B verification and rollback — issues #54–#57

All data/results are synthetic. This stack is reviewable implementation and verification work,
not a release certification or authorization to merge/deploy. Per the user's override, #53 is
complete and [PR #72](https://github.com/bwold001/pdp-datathon--uncf/pull/72) is the reused baseline.
Starting revision: `46fd9eb6ce8e8887323e09ab3342dc3c2ff2a397`. #72 was unmerged at inspection.

## Stack and review order

| Order | Issue / PR | Head | Immediate base |
|---|---|---|---|
| 1 | #54 / [#73](https://github.com/bwold001/pdp-datathon--uncf/pull/73) | issue-54-student-year1 | issue-53-release-a |
| 2 | #55 / [#74](https://github.com/bwold001/pdp-datathon--uncf/pull/74) | issue-55-bounded-exploration | issue-54-student-year1 |
| 3 | #56 / [#75](https://github.com/bwold001/pdp-datathon--uncf/pull/75) | issue-56-mixed-plans | issue-55-bounded-exploration |
| 4 | #57 / this PR | issue-57-release-b | issue-56-mixed-plans |

Read `analytics/exploration/datasets.py`, `catalog.py`, `operations.py`, then `plan_service.py`,
`api/tests/test_mixed_exploration.py`, the v2 chat owner, and the result cards. #57 also corrects
the independently recorded gateway course-threshold mismatch and removes obsolete chat code.

## Implemented operation inventory

All versions are 1 except `gateway.course_outcomes` version 2:

- Defined: retention.rate, persistence.rate, dfw.rate, dfw.course_list, dfw.course_detail,
  credit_completion.ratio, credit_momentum.summary, gateway.math_completion,
  gateway.english_completion, gateway.course_outcomes, student_paths.summary.
- Distinct legacy adapters: legacy.graduation, legacy.entry_major_retention, legacy.annual_enrollment.
  Their horizons, program attribution, perspectives and coverage rules remain in use.
- Exploration: grouped_summary, mean_comparison, correlation.
- measure_variant is registered to return unavailable/unsupported_evidence for
  gateway.cohort_completion_c_or_better. It does not substitute course-taker outcomes.

The normalized dictionaries describe highest year-one gateway grades, not first-attempt grades;
P would qualify. Independent source profiling found required/completed records with blank or
contradictory grades (math: 3 blank + 3 F; English: 1 blank + 8 F + 1 W + 1 grade 0.7).
Equivalent classification over the baseline cohort denominator is therefore not established.
Reconciled completion/highest-grade evidence and validated non-attempter eligibility are the
missing prerequisite. A C/D flag alone cannot supply a C-or-better outcome.

The separate course-outcome calculation now uses >=2.0 or P, preserves term/first-attempt
rules, and labels grades from 1.0 to below 2.0 as Below C. Required cohort completion remains
>=1.0 or pass with its existing denominator. Gateway story fixtures were regenerated from the
actual API, including sparse courses previously omitted by old fixtures.

## Dataset, methods and visibility

student_year1 version student_year1-1 has exactly one private student/cohort unit. Cohort
credits are independent of course sums. Actual enrollments are preaggregated on both join keys;
repeated attempts count separately. Dashboard filters and school/federal answers are reused.
Unknown/unresolved term or delivery evidence and no year-one records are excluded from online
features; known F/H records with no online enrollment give a real zero. Exposure is observed,
not certified whole-year completeness. The unknown-year edge fix lives in #54 and is propagated.

Feature versions are 1; missingness is complete-cases-1. Feature/missingness/dataset versions,
method versions, source/build/pipeline/configuration/policy identities and ordered dependencies
participate in replay. Supported methods grouped_summary, mean_comparison and pearson use version 1.

Registered grouping IDs: online_count_0_1to2_3plus, retention_outcome_school,
retention_outcome_federal. Exactly one grouping is enabled per step; no two-dimensional
cross-product is registered. Numeric pairs are the catalog's five symmetric pairs: earned/
attempted credits, and online count/share each paired with earned/attempted credits.

Earned and attempted means have separate n/missing counts. Pearson uses paired complete cases,
requires n>=2 and nonzero variance. Means and differences allow n=1. Online differences are
1–2 minus 0, 3+ minus 0, 3+ minus 1–2; retention is not-retained minus retained. Missing inputs
retain valid sibling evidence. Unknown/unobservable retention is never not-retained.

Every nonempty group and one-unit exclusion stays visible, including under obsolete settings
10/100. Final projection validates metadata and excludes identifiers. UI minimum settings cannot
restore privacy hiding. Historical omitted values remain unavailable until recomputed; null is
never reconstructed as zero. No minimum-size or repeated-query inference protection is claimed.

Bounds: four plan steps; one registered grouping; twenty occupied groups (all sizes count);
500,000 source enrollments per step; ten seconds per step within the existing 75-second chat
budget. Twenty/21 enforcement is independently tested at the group-bound owner; currently
registered groupings occupy at most three groups. No partial source/group truncation is used.

## Executed validation and exact limits

- #54 `17a88e73eda400eb40cd26fef90f379949ae9477`: 16 dataset cases; make check-fast 1,117 passed /
  52 skipped; make check 1,124 passed / 76 skipped. Root manifest/quality checks passed.
- #55 `bcb2c5e67b10548265fdfe76c263598c2a896623`: propagated dataset fix; analytics 238 passed /
  1 skipped. Previous full check on its owner tree passed 1,156 / 76 skipped.
- #56 `d7d81b2dfbeed61c1a2f7baad676928fb3675922`: propagated fix; analytics/API 387 passed /
  13 skipped. Its prior full check passed 1,177 / 76 skipped; backend 128 / 5 skipped.
  Published checks passed, including configured PostgreSQL and Linux browser checks.
- Final #57 owner tree: make check-fast 1,171 passed / 52 skipped. After creating the previously
  absent local extract, make check passed 1,201 / 53 skipped. This activates real-data slow
  regressions, including an independent SQL recount of over 5,000 measure/group combinations.
  The stale threshold-ten expectation in that recount was corrected, not bypassed.
- Final backend: 115 passed / 5 skipped; Ruff lint and formatting passed. The repository's
  current task is api:test (SQLite default); api:test-sqlite no longer exists after #71.
- Client ESLint/TypeScript passed. Production compilation succeeded; Next.js 16.4.2 emits a
  security advisory interruption and a retry succeeded. The advisory remains a release concern;
  no dependency upgrade or security check disabling was performed.
- Playwright Chromium installed; local Storybook could not launch because macOS denied its
  Mach-port registration (1100), before loading any story. Local browser checks are unverified.
  Use current-head Linux CI browser results, not this failed local launch, for browser evidence.
- Four actual HTTP receipts were rendered through React's actual EvidenceCard; exact rates,
  signed differences/correlation, sample sizes and synthetic notices were verified. This SSR
  check supplements browser testing and does not certify interactive behavior.
- A fresh synthetic extract was built only after confirming no default database existed.
  It has 100,951 source enrollments. A real four-step 2023-24 plan took about 0.565 seconds;
  direct and confirmed-chat results, versions and fingerprints agreed. No developer DB was reset.
- Pure statistical benchmarks on 100,000 synthetic units: summary 0.0563s, comparison 0.0364s,
  Pearson 0.0250s. Those timings exclude database reads; the four-step timing includes reads.

Fresh extract snapshot: `0a35f6adac5843ef7d9ff772d7d986e4c18f22da0bd75fde6d04f723918f0f76`;
source `16dd9a18ad20c5c6d79128bf39a8651bd309242a79c0a89ccdaa38110d3a0a74`;
pipeline `720f2e39d124adeebcc5efa26fda4df43c6d1e671bf8c4a45dd19e36916975b7`;
normalization `938b25ceb9fb9421ce26c7f39dd6109bc71af7febadbe1ee21e5daaf5725a22b`.
Equal source hashes alone are not used to claim normalization equivalence. Snapshot/build and
configuration identities were compared for direct/chat parity. Deployed preview parity is unverified.

## Live model gate

The fixed release_b_prompts.json has 41 cases, reusing applicable Release A cases and adding
online count/share/period ambiguity, exploration, official retention plus characteristics,
small groups and unsupported causal/variant requests. The shared runner/scorer records model,
revision, suite hash, routing, constraints, clarification and unsupported outcomes separately.
Ordinary tests remain scripted and cannot substitute for a production-model evaluation.

Run from the Playground backend:

```sh
uv run python -m scripts.evaluate_release_b --model "$UNCF_CHAT_MODEL" \
  --database ../../normalized-data-model/output/pdp.sqlite \
  --output /tmp/release-b-model-evaluation.json
```

The local attempt used repository default openai/gpt-4.1, not a verified deployed model ID.
OPENROUTER_API_KEY was absent: **0/41 live cases ran**, status unverified, gate_passed false.
Production interpretation remains a release blocker. No key values are stored in reports.

## Transport cleanup and rollback

Chat paths /api/v1/chat and /api/v1/uncf/chat remain routed, but require the v2 body. Obsolete
unversioned chat requests now return a typed 422 invalid_plan. Removed: old three-analysis
prompt/tool dispatcher/contracts, its unused client service and CalculationCard, and obsolete
v1-only tests. SDK mocked-HTTP, configured-source parity and actual cancellation/cleanup tests
were migrated to v2. Dashboard URLs, /results, deterministic APIs, legacy calculation owners,
metadata MCP functions, provider selection and Vercel entrypoints remain. The general SQL MCP
tool stays dormant. No feature flags or database migrations were introduced.

The rollback candidate reuses #53's recorded compatibility evidence for merged #71 revision
cf84f8e02369cae50d3972e242c2ba1fd6a03c99 (21 legacy/deployment checks). This is a code candidate,
not a verified previous production deployment. The actual known-good deployment ID/revision is
unavailable, and no deployment/rollback rehearsal occurred in this task.

Operator steps, requiring separate deployment authorization:

1. Establish the previous immutable production artifact and its matching client/server revision;
   verify its environment, normalized schema/build metadata and coverage configuration.
2. Redeploy the complete matched artifact. Do not combine an old server with a new chat client.
   No destructive data reset is needed; analytics reads the same normalized schema.
3. Allow bounded in-flight cleanup; do not switch protocols mid-response. Check the old artifact's
   supported chat contract and dashboard/direct API behavior against the same synthetic snapshot.
4. Release B replays require their exact versions/snapshot. Refuse unavailable versions instead
   of replaying with substituted rollback code. Record the deployment ID and smoke-check evidence.

Release B is not certified until live model evaluation, deployed snapshot parity, current-head
required CI, security-advisory assessment and an established rollback target are recorded.
