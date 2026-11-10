# Student success chat calculations

The chat is a synthetic-data demonstration. Its numbers are not findings about real students or institutions. The model selects approved operations; Python calculates the results, and the browser renders the returned receipts. Model-written numerical prose is not displayed.

## Definitions

| Analysis | Calculation and population | Boundaries |
| --- | --- | --- |
| Graduation, any program | First qualifying cohort-institution completion / eligible entrants who entered the selected chemistry program, in the selected credential population and cohort | Four-year, six-year and completion-to-date views are separate. Unknown credential eligibility, entry program and completion timing are excluded explicitly. |
| Graduation, selected program | Qualifying completions with inferred final-semester program in the selected chemistry set / eligible chemistry entrants with known completion-program outcome | A graduate with unresolved major is an excluded unknown, not a known non-chemistry completion. |
| Graduate composition | Inferred chemistry graduates who entered in chemistry, switched in, or have unknown entry program / all inferred chemistry graduates in that cohort/window | This is composition, not a graduation rate. Unknown completion-program evidence is excluded explicitly. |
| Retention | Retained students / students with known retention outcomes, overall and by first-term major | Uses the existing PDP retained flag: enrolled again in the next academic year or a credential earned by then. Unknown outcomes are excluded; unknown programs remain a labeled group. The starter's 2024-25 cohort is provisional. |
| Enrollment | Distinct student IDs within academic year, term program and ethnicity | Latest two declared complete years, across entry cohorts. Actual course enrollments only. Students changing programs can appear in multiple programs; program totals overlap. Ethnicity never substitutes race. |

The authoritative definitions live in `uncf/analytics/definitions.py`. Each receipt includes their version, formula, population, grain, actual counts, exclusions, parameter choices, source-load timestamp, source stamp, extract cutoff and limitations. Rates use numerator / denominator, rounded to four decimal places in the data contract. Count-only enrollment has no denominator or invented rate.

## Program and credential evidence

Entry major uses `cohort_membership.program_of_study_term_1`, not end-of-year major or course subject. Enrollment uses `course_enrollment.term_program_of_study`. Queries join course enrollments and cohort membership on both student ID and cohort.

A complete six-digit CIP code is preserved; a `40.0501` representation can be normalized to `400501`. Truncated or ambiguous values remain unknown. Normalized model corrections are not repeated in this layer.

Chemistry has two explicit choices: Chemistry, General (`400501`) and the curated chemistry family (`40.05`). The family catalog follows [NCES CIP 2020](https://nces.ed.gov/ipeds/cipcode/cipdetail.aspx?cipid=90775&y=56), including analytical, inorganic, organic, physical, polymer, chemical physics, environmental, forensic and other chemistry programs. Chemical engineering and enrollment in chemistry courses do not establish a chemistry major. Catalog entries and provenance are maintained in `uncf/programs.py`.

Completion timing uses the credential-specific `first_year_to_*` field and checks it against its corresponding latest-credential field. A zero in both means no reported qualifying award through the declared extract window; a missing, contradictory or unobserved year is unknown. Bachelor, associate and certificate populations use `B`, `A` and `C`, respectively. Other or unknown credential-seeking codes are not silently mapped into those populations.

`time_to_credential` describes the earliest credential, rounded to a decimal year. It cannot locate an exact award semester or identify a later bachelor's completion. The starter normalized schema contains no credential-specific award semester/date. Therefore the database-backed service currently leaves graduation-program attribution unknown. It still supplies independently supported any-program completion results when follow-up is certified. Do not enable composition values by treating the last recorded course semester as an award semester.

The final-program helper requires resolved award-semester evidence, ignores UNKNOWN terms, and rejects conflicting or missing programs in the relevant final semester. If a future institution-approved source supplies precise award evidence, integrate it deliberately and test its semantics before enabling this attribution in the service.

## Certifying coverage

`uncf/config/analytics.yaml` is the shared source of coverage declarations. `UNCF_ANALYTICS_CONFIG` can select another server-side configuration file. It is never a browser or model parameter.

The supplied configuration leaves complete years, cohort follow-up and cutoff unset: the mock extract does not certify these. This intentionally yields unavailable annual enrollment and completion-to-date results and uncertified four/six-year states. Retention still uses the stored outcome flags. Do not infer completeness from today's date, the maximum course year, credit-year availability or one observed graduate.

For an independently verified **test fixture only**, a declaration looks like:

```yaml
complete_academic_years: ["2022-23", "2023-24"]
cohort_followup_years: {"2022-23": 4}
cutoff: "2026-06-30"
provenance: "Hand-counted synthetic fixture; not a certification of the shared mock extract"
suppression_threshold: 10
provisional_retention_cohorts: ["2024-25"]
```

Require provider/analyst evidence before making corresponding declarations for a campus extract. Each horizon is evaluated independently. Completion to date is descriptive; it is never labeled a mature four/six-year rate.

## Missing and hidden results

Zero is a computed value. Unknown means the available evidence cannot establish an outcome. Unavailable means a required source or certification is missing. Not yet observable means whole-cohort follow-up is not certified for the horizon. Provisional means a returned retention result may change with follow-up. Suppressed means numerical evidence has been hidden.

Before either the provider or browser sees a receipt, a conservative projection hides all linked numerical breakdown rows when a denominator, positive numerator, complementary count, enrollment count or exclusion falls below the configured threshold. An independently safe overall retention result can remain visible while all program breakdown counts are hidden together. Hidden rows carry no counts, rates, substitutions or exclusion counts. This prevents simple within-table complementary disclosure at the expense of hiding more results. It is not a production privacy guarantee across arbitrary repeated queries, releases or external data. This demonstration must remain synthetic-only.

## Adding an analysis

Keep institution-specific program logic in `uncf/analytics/`. Define a typed request and versioned definition, implement the deterministic calculation, add hand-counted tests, and dispatch through the service. Register the narrow model tool contract only after direct API and chat parity is verified. Do not expand upstream measure enums merely to accommodate a team-specific program analysis. Existing Results routes and clients keep their current contract.
