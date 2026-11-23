# Release A exit-gate evidence — issue #53

PR #72 is a reviewable verification/tooling change based on merged PR #71. The **Release A exit gate remains blocked** by the separate semantic and environment checks below. Approving this PR does not certify Release A or authorize deployment. All fixtures and results are synthetic.

## Revision and supported contract

Merged baseline and locally verified rollback candidate: `cf84f8e02369cae50d3972e242c2ba1fd6a03c99`
(PR #71, Remove unused Playground starter code). The combined verification tree is
`f33a68f8f68841f12469cc2a63dbf1215391d734` plus documentation-only handoff updates.
Verification changes are on `issue-53-release-a`; the PR head is the release candidate,
not an already deployed revision. No source calculations or transport contracts
change in this PR. The actual production revision/deployment ID has not been established.

PR #71 removes the Sandbox, Workbench and starter database stack. This PR preserves that removal:
local backend checks use `mise run api:test` and disposable SQLite fixtures, without Docker,
Alembic or `TEST_ON_SQLITE`. The default runtime reads the bundled normalized SQLite extract;
configured PostgreSQL support still needs its own integration evidence. No removed starter code,
dependencies, database services or old test task are restored.

The inventory is eleven defined operations and three legacy adapters, each currently version `1`:
`retention.rate`, `persistence.rate`, `dfw.rate`, `dfw.course_list`, `dfw.course_detail`,
`credit_completion.ratio`, `credit_momentum.summary`, `gateway.math_completion`,
`gateway.english_completion`, `gateway.course_outcomes`, `student_paths.summary`,
`legacy.graduation`, `legacy.entry_major_retention`, `legacy.annual_enrollment`.
Use catalog schemas and result-policy references rather than treating labels as interchangeable.
No exploratory executor or new feature flags are introduced. Missing columns are named by catalog
prerequisites. Certified follow-up/complete-year coverage remains request-specific; do not invent it.

**Semantic blocker:** `measures/registry.py` describes `gateway.course_outcomes` as >=2.0 or P,
but `measures/breakdowns/gateway_courses.py:gateway_passed` uses `GATEWAY_PASS_AT=1.0`.
The baseline tests explicitly expect a first-attempt 1.5 to pass. Issue #53 requires >=2.0 or P.
The release evaluator records expected versus actual grade boundaries and keeps `gate_passed`
false for this mismatch. Resolve the shared course calculation, grade presentation, affected fixtures
and version semantics before release. Requirement-based cohort completion retains its distinct
>=1.0 or pass definition; non-attempters and denominators must not be transferred between them.
The acceptance ledger records the release requirement, not a claim that that gate passes today.

## Independent arithmetic and surface evidence

- `measures/tests/test_chat_v2_baseline.py`: two student ratios 1/2 and 1 give numerator 1.5,
  denominator 2, mean .75 (pooled credits would be 2/3). One student with grades .69, .70, 1.99,
  2.00, P, W, I and unknown has 3 DFW enrollments / 6 classifiable enrollments = .5,
  distinct student n=1. This preserves the current DFW boundary (1.7); I/unknown are excluded.
- Existing owner tests cover all fourteen operations, school/federal retention, credit tiers,
  fractional numerators, required non-attempters, retakes and independent legacy horizons.
  Passing baseline tests alone do not establish the required gateway course threshold.
- `test_release_a_same_snapshot_json_csv_api_and_chat` uses the same normalized synthetic fixture
  through real HTTP serialization: every size 1–9 has zero retained / positive n, zero rate,
  and matching dashboard JSON, CSV, direct v2 and confirmed-chat counts. Both old threshold
  settings 10 and 100 are exercised, including legacy coverage configuration.
- Direct v2 and chat receipts must match source metadata, all computation versions and fingerprints.
  The fixture explicitly installs source hash `c` repeated 64 times, pipeline `a` repeated 64 times,
  normalization `b` repeated 64 times, generation `00000000-0000-4000-8000-000000000001`.
  These are fixture identities, not production certifications. Dashboard v1/CSV have no full v2
  manifest contract; the test binds them to the same physical fixture. This is local parity,
  not a preview/production normalization comparison.
- Existing HTTP and chat tests cover whole-plan refusal, unsupported exploration, exact confirmation
  without another provider call, stale scope, missing snapshot/version replay, cancellation,
  database interruption, bounded independent refusals and partial outcomes. Client stories own
  reset/new-question/late-response and card representation checks.

## Fixed production-model interpretation evaluation

The committed `playground/server_application/tests/fixtures/release_a_prompts.json` contains 34
fixed Release A prompts. It covers all fourteen IDs, required filters, missing cohort/retention
choices, both gateway meanings, credit tiers, online count/share refusals, causal/custom requests,
and explicit dashboard context/overrides. Expectations are operation IDs, constraints and
clarification fields, never exact prose. Deterministic state transitions remain scripted tests.

From `playground/server_application/`, after `mise run api:install`, run:

```sh
uv run python -m scripts.evaluate_release_a \
  --model "$UNCF_CHAT_MODEL" \
  --database ../../normalized-data-model/output/pdp.sqlite \
  --output /tmp/release-a-model-evaluation.json
```

Use the actual configured production model and a known synthetic snapshot containing the required
schema/cohort/course choices. The report pins revision, dirty state, suite hash, model and catalog
snapshot/configuration/implementation stamps. It reports routing, retained constraints, necessary,
missed and unnecessary clarification, unsupported outcomes and absence of execution separately.
No proposal is confirmed or executed. Each case has a 75-second deadline and a request-scoped SDK.
Any failed case or boundary check prevents a successful evaluation exit. A passing evaluation does not establish the other release gates. Rerun when the model changes.

The local attempt selected repository default `openai/gpt-4.1`; the key was unavailable to the
local process, so **0/34 live cases ran**, status unverified, gate_passed false. The user reports an
OpenRouter key configured in Vercel. This connection cannot access the UNCF project to verify its
environment scope/model or run that deployment evaluation; this is not evidence that the deployed
key is absent. No credential values are written to reports.

## Rollback without feature flags

A separate detached checkout of `cf84f8e02369cae50d3972e242c2ba1fd6a03c99` passed the existing
`test_chat_deployment.py`, `test_uncf_chat.py` and `test_student_success_tools.py` suites:
**21 passed**, using the post-#71 Python 3.14 backend environment and disposable SQLite fixtures.
That establishes local v1 route/confirmation compatibility on this candidate; no deployment
rollback rehearsal occurred. The candidate still shares the gateway semantic blocker above.

Relative to merged PR #71, this PR leaves `vercel.json`, dependency locks, loader/schema/pipeline,
raw inputs, coverage config and runtime environment contracts unchanged. PR #71 itself changed
the dependency locks and default database selection; the rollback candidate includes those changes. No migration or destructive reset is needed to
restore the candidate. Historical v2 receipts require the original snapshot, implementation,
operation, configuration and policy versions for replay; rollback does not make missing versions
available and must never silently recalculate on another snapshot.

Operator steps, only after separate authorization:

1. Record the proposed release SHA, all three service deployment IDs, actual current known-good
   SHA/deployment IDs and environment/data stamps. A locally passing commit is not proof of a
   known-good production deployment. Verify legacy v1 behavior on that actual target first.
2. Verify the previous deployment includes compatible frontend, Results API and chat services,
   rewrites/assets, bundled synthetic extract, model/key configuration and coverage declarations.
   Compare normalization/pipeline/configuration stamps in addition to source hashes. Preserve
   external databases and credentials; do not reset them or toggle a rollout switch.
3. In the hosting deployment interface, restore/redeploy the recorded known-good revision for the
   coordinated services. Avoid switching protocols mid-response; allow in-flight requests their
   bounded cleanup (75-second app deadline, 90-second client deadline, 120-second hosting limit).
4. Verify v1 analyses, both chat URLs, Explorer JSON/CSV and assets. Verify missing-key failures and
   deterministic endpoint independence, then check new v2 scope/receipts if that target supports v2.
5. Record restored deployment IDs, stamps, checks and unresolved failures. If compatibility cannot
   be established, stop promotion and retain the incident evidence; do not invent a successful rehearsal.

## Remaining release gates

Resolve the gateway definition mismatch; run the configured live model set; verify PostgreSQL in
its required environment; complete browser/preview parity and identify/test the actual known-good
deployment. No PostgreSQL URL was configured, and no developer database was reset. PR #71 was merged upstream; PR #72 has not been merged. No production deployment or rollback
was performed in this work. Keep issue #53 open until required gates pass.

## Commands and results (November 23, 2026)

These are fresh checks of the combined post-#71 tree above; the pre-#71 counts are superseded. Root requirements were
installed from `requirements.txt` in `.venv`; Playground dependencies were synced from `uv.lock`,
and client dependencies installed with `bun install --frozen-lockfile` (offline hardlink install
completed from the populated cache). Toolchain: root/backend Python 3.14.8,
Bun 1.4.3, Node 24.22.2, uv 0.13.0, mise 2026.11.12. No tracked lock/configuration files changed.

| Command/check | Result |
| --- | --- |
| Root targeted `pytest measures/tests analytics/tests api/tests -m 'not slow' -q` | 522 passed, 7 skipped, 23 deselected |
| `make check-fast` | 1,101 passed, 52 skipped; manifest and quality checks passed |
| `make check` | 1,108 passed, 76 skipped; manifest and quality checks passed |
| `mise run api:lint` | Ruff lint and formatting passed |
| `mise run api:test` | 127 passed, 5 skipped |
| `mise run web:lint` | ESLint and TypeScript passed |
| `mise run web:build` | Compilation, types and seven-route generation passed; initial command stopped on a Next.js security-advisory check; the same task passed on its single retry, without dependency changes |
| `mise run web:test-storybook` | Chromium installed; launch failed with Mach-port `bootstrap_check_in` permission denied (1100). Browser assertions did not run; unverified |
| Real serialized receipts through React `EvidenceCard` static markup | Nine zero-rate receipts retained n=1–9, result policy, computation fingerprint and synthetic notice. This does not replace browser/interaction verification |
| Detached rollback candidate's legacy/deployment tests | 21 passed; revision/compatibility check only |
| Live model evaluation | 0/34 ran: Vercel key unavailable to the local process; unverified. Independent gateway boundary check failed as documented above |
| PostgreSQL | No configured integration URL; unverified. SQLite does not establish PostgreSQL parity |

The Next.js diagnostic reported a known vulnerability in the pinned framework version. Dependency
upgrades are outside this verification change; assess that advisory before deployment. No automated
upgrade, production operation or database reset was performed.
