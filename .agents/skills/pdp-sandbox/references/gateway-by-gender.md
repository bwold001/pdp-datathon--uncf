# Gateway completion by gender

Use this as the reference path when adding a computed Sandbox chart from the normalized model.
The source of truth is the [data-model gateway query](../../../../normalized-data-model/README.md#8s-gateway-question-in-one-join)
and its test at `normalized-data-model/tests/loader/test_gateway_query.py`.

## Question and expected answer

For the `2022-23` cohort, what share of students required to take gateway math completed it, by
gender? This fits the shared Measures route:

```text
GET /sandbox/measures/by-group?measure=gateway_math&cohort=2022-23&group_by=gender
```

| Group | Completed | Required (`n`) | Rate |
| --- | ---: | ---: | ---: |
| F | 162 | 620 | 26.1% |
| M | 116 | 456 | 25.4% |
| UNKNOWN | 25 | 72 | 34.7% |
| X | 1 | 1 | 100.0% |

The first three rows are exact known answers from the model. The final row is the unsuppressed
model result; a client-facing Measures response hides it because its denominator is under 10,
returning `rate: null`, `n: null`, and `suppressed: true` instead. These are synthetic-data values.
A production institution feature must run the same logic over its approved institutional data.

## Server shape

Create a row schema with the display label, rate, and denominator:

```python
class GatewayByGenderRow(BaseModel):
    group: str
    rate: float | None
    n: int | None
    suppressed: bool
```

The endpoint accepts typed `measure`, `cohort`, and `group_by` query parameters. For
`gateway_math`, it queries `cohort_membership` joined to `student` on `student_id`, limits to the
requested cohort, and counts gateway-math `C` out of `C` and `D`. Its `ChartMeta` names the
modeled fields and says the source is synthetic.

Add the endpoint path to `ENDPOINTS` in `playground/server_application/tests/test_sandbox.py`, then
assert the exact F and M rows above, plus the suppressed X row. Add a second test that an
unsupported cohort returns FastAPI's 422 validation response.

## Client shape

In the matching Sandbox page:

1. Put the supported cohort values and display labels in `data.ts`.
2. Build a stable loader from the selected cohort query parameter.
3. Use `ChartCard` and an existing bar or grouped-bar component. Surface `n` alongside the rate.
4. Keep labels and formatting in `chart-config.ts`; do not repeat the measure calculation in the
   browser.

When the shared success-measures calculation is available, use its `gateway_math` result rows
rather than reimplementing this query.
