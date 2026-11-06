---
name: pdp-sandbox
description: Add a Playground Sandbox endpoint and chart from the PDP data model. Use when asked to chart or add a Sandbox page for a PDP measure.
---

# pdp-sandbox

Build institution-focused features in the Playground Sandbox from the normalized PDP data model.
Sandbox is the development and validation workspace; follow the deployment boundary at the end of
this skill when carrying a verified feature into an institution application.

## Start with the data model

Use the normalized tables, not `data/raw/`, as the source for a feature. The data model applies
the shared corrections once, so every squad gets the same race labels, gateway values, and credit
years. Read [Things to know before you query](../../../normalized-data-model/README.md#things-to-know-before-you-query)
before writing a query.

Use [`pdp-data`](../pdp-data/SKILL.md) only when you need to map an original ARF column or
dictionary term to its modeled field. Do not repeat the raw-file joins or cleaning in a Sandbox
feature.

Before writing the route, state:

- the question and intended measure;
- the data-model tables and fields used;
- the chosen filters and their allowed values;
- whether the loaded model can actually answer it.

If the model cannot support the question, say so. An interface-only fixture may be useful for
testing a workflow, but label it clearly and do not present invented values as computed results.

## Build a focused institution feature

Keep model queries and aggregation in FastAPI. The browser receives only a typed, aggregated
response. Use the Playground server's read-only data-model connection when it is available; do not
add another raw-file loader or duplicate the model's cleaning steps.

Follow the existing paired Sandbox layout:

```text
playground/server_application/app/sandbox/<topic>/
  schemas.py       typed response rows
  routes.py        typed query parameters and endpoint
  ...              query and aggregation over the data model, or a clearly labeled fixture

playground/client_application/src/app/sandbox/<topic>/
  data.ts          typed loader matching the endpoint
  chart-config.ts  field-to-chart labels and mapping
  charts.tsx       existing Sandbox components and filter state
  page.tsx         focused explanation of the question and interaction
```

Mount the server router in `app/sandbox/router.py` and add the client route to `src/lib/routes.ts`
when the feature needs a shared link. Use the starter reference implementation in
[`playground/README.md`](../../../playground/README.md#build-a-sandbox-feature) and the
client/server README steps instead of creating a parallel pattern.

## Turn model rows into chart rows

Turn the validated question into the smallest chart-ready aggregate in the server:

1. Query the modeled tables needed. Follow their documented join keys, including `student_id` and
   `cohort` for course enrollments joined to cohort membership.
2. Apply selected filters before calculating the measure. Validate query parameters against a
   finite set of supported values rather than passing arbitrary column names or expressions through
   the API.
3. Use the model's stored `UNKNOWN` values and documented corrections as-is. Keep the denominator
   visible in the measure definition when it affects interpretation.
4. Group into one response row per chart point or bar, using simple field names such as `cohort`,
   `program`, `count`, or `completion_rate`.
5. Compute rates on the server as numerator divided by the filtered denominator. Do not calculate a
   rate by averaging already-aggregated percentages in the client.

Keep domain computation in the server. `chart-config.ts` may map returned fields to labels and
formatters, while `charts.tsx` selects an existing chart component and owns only UI state such as
filter controls.

For a concrete schema → route → loader → chart path, read
[the gateway-by-gender reference](references/gateway-by-gender.md). It uses a known 2022-23 answer
from the data-model tests and shows the endpoint test the feature should add.

## Shared success measures

For retention, persistence, gateway math, and gateway English, use the shared success-measures
contract once [#46](https://github.com/devcolor/pdp-datathon-starter/pull/46) merges: it provides
`run_measure` and rows with numerator, denominator, rate, suppression, and notes. Until then,
build a nonstandard exploration directly from the data model rather than independently defining a
second version of a shared measure.

## Response and chart contract

Reuse the shared `ChartResponse` and `ChartMeta` shape. For each chart, include:

- a plain-language title and description;
- `fields_used` using the dictionary names or clear field labels;
- selected filters in `meta.filters`;
- definitions for non-obvious measures;
- `source: "synthetic"` for a value computed from the shared model, or `source: "mock"` for an
  invented fixture.

Return `n` beside a rate. If a group is suppressed, return `rate: null` and `n: null`; never
replace those values with zero or drop the group.

Use existing `ChartCard`, `KpiGrid`, `BarList`, `TrendChart`, or `GroupedBarChart` before creating
a new chart component or adding a charting library. Make filter selections typed query parameters
and have the displayed chart, filters, and source link describe the same response.

## Verify

Put new endpoint tests in `playground/server_application/tests/test_sandbox.py`: add the path to
`ENDPOINTS`, then assert known numerator, denominator, rate, and suppression values. Do not rely
only on asserting that two filters return different rows.

Run the checks that apply:

```bash
cd playground
mise run api:test-sqlite
mise run api:lint
mise run web:lint
mise run web:build

cd ..
make check
```

`make check` validates the shared data and normalized model; it does not test the Playground. The
Playground CI job runs the API and web checks. If an endpoint needs the loaded model, ensure that
job loads the SQLite model before `mise run api:test-sqlite`, so the known-answer test runs in CI.

## Deployment boundary

The shared model and its results are synthetic. In the UI and any write-up, say they are not
findings about real students or institutions. Sandbox routes are disabled in production; carry a
verified feature's contract and UI into the institution application's production routes, using
institution-approved data.
