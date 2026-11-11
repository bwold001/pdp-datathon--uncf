# Chat v2 planning and immutable receipt pages

Issue #52 starts from reconciled #51 commit `67215e7bbb692c71d8aa48fb9513fadc877a2393`;
The branch was updated to dependency head `c6d4987d4b8dce6949cf2bc7537652105f648012`
after the grade-scale, CI and Share Insight merges. Main was initially inspected at `563d9fb48b500fcf69af665f28922c01eed836d3`.

The Playground client sends `protocol_version: 2` to `/api/v1/uncf/chat`.
Omitting the version retains the v1 request/response contract. The server exposes
catalog search, registered operation details and whole typed plan proposals to the
provider. No proposal tool calculates. Numerical prose is discarded. The shared
PlanService replaces provider choices with server choices, materializes defaults,
validates the entire plan and executes confirmed requests. No new flags are used.
The fourteen registered defined/legacy operations remain the Release A boundary.

Clarification carries the complete ProposedPlan and selects one step ID and allowed
parameter key. Revalidation rebuilds current choices before selection. Confirmation
carries the exact ExecutablePlan, including catalog and snapshot references, without
a provider call. A changed reference returns updated review state. New questions and
reset invalidate pending client requests; late responses cannot restore old state.
Dashboard context is optional typed request input and is supplied to the provider
only when actually sent. This standalone chat does not invent dashboard context.

## Representation decision

Use explicit immutable receipt pagination, preserving existing scalar-per-row paths,
values, units, component identities, statuses and exclusions. This avoids regrouping
heterogeneous page components with different denominators.

A table payload's `rows` contains page one (at most 200 rows). Its additive `pages`
contains up to 63 subsequent typed pages in order. Only the final page may have fewer
than 200 rows when there are multiple pages. The total is `len(rows)` plus the sum
of subsequent page lengths; every row occurs once. All pages are calculated once
within the confirmed plan's read snapshot and serialize together in the receipt.
The client switches local pages without API calls, recomputation or changing scope.
Receipt source, computation fingerprint, versions and execution identity bind every
page. Historical/missing rows retain an optional component `path` without omitted
numerical inputs. Empty collections remain explicit evidence.

Page adapters refuse the entire result beyond 12,800 scalar rows and explain how to
narrow scope. Existing scalar breakdowns and legacy tables retain their 200-row
resource refusal. There is no silent truncation or exploratory operation added for
rendering. Consumers must read `pages` as well as `rows` for page-operation tables.

Cards render count/rate/mean/comparison/correlation/table payloads, including signed
values, zero rates, small samples and exclusions, exact scope, definitions, source
coverage and build/pipeline/policy versions. Historical suppressed receipts require
recomputation; unknown, unavailable, unreported and unobservable remain separate.
All data and displayed results are synthetic demonstrations.

## Verification

Scripted-provider tests live in `playground/server_application/tests/test_chat_v2.py`.
They use real normalized synthetic fixtures with independent expectations (12 DFW
rows / 24 classifiable enrollments = .5). Stories cover small groups 1–9, zero,
negative comparison/correlation, payload types, historical/missing states, partial
failure and immutable page navigation. Provider interpretation with a live model and
PostgreSQL integration require separate configured environments.

V2 credit-momentum evidence includes the known-retention denominator separately
from tier membership and credit-share denominators. These are copied from the shared
owner helpers; v1 pages keep their existing shape. Typed page rows carry an additive
`applicable_n` column for the rate/mean denominator when supplied by the owner.

Validation on the reconciled branch: `make check-fast` passed (1,099 passed, 52
skipped); `make check` passed (1,106 passed, 76 skipped). Playground Ruff lint and
format checks passed; SQLite tests passed (138 passed, 5 skipped). Mise is unavailable
on this host, so the declared underlying commands ran directly using Python 3.14.8,
Bun 1.4.3 and Node 24.22.2. Frozen-lockfile offline install verified 905 installs
across 1,046 packages. Client lint, type checking and production build passed.
Actual serialized synthetic receipts rendered through the React cards passed static
markup checks for sample sizes 1–9, zero rates, units and synthetic notices, plus
negative comparisons/correlation and sample sizes.

Storybook's browser assertions and visual QA remain unverified: Chromium installed
in the workspace but macOS denied Mach-port registration (1100/SIGTRAP) before any
stories ran. PostgreSQL integration is unverified without `PDP_TEST_POSTGRES_URL`;
no existing developer database was reset. No live-provider evaluation, merge or
deployment was performed.
