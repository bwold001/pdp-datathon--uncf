---
title: Pre-aggregating multi-term supplementary datasets before joining cohort tables
date: 2026-11-01
category: best-practices
module: metadata-assistant
problem_type: best_practice
component: data_model
severity: medium
tags: [squad-metadata, supplementary-data, sql, joins, holds]
---

# Pre-aggregating multi-term supplementary datasets before joining cohort tables

## Problem

When joining supplementary institutional datasets (such as `registration_holds`, `support_services`, or `financial_aid_detail`) to `cohort_membership` or `student`, a student may have multiple records across terms or academic years. Performing a direct join produces a 1-to-many Cartesian row multiplication that artificially inflates cohort counts and distorts retention or completion rates.

## What didn't work

Joining `registration_holds` directly on `student_id`:

```sql
SELECT cm.cohort, COUNT(*), AVG(CASE WHEN cm.retention THEN 1.0 ELSE 0.0 END)
FROM cohort_membership cm
JOIN registration_holds h ON cm.student_id = h.student_id
GROUP BY cm.cohort;
```

If a student had three separate holds across fall and spring terms, that student was counted three times in the cohort totals.

## Solution

Pre-aggregate hold records per student and academic year using a Common Table Expression (CTE) through the `term` table before joining to `cohort_membership`:

```sql
WITH pre_aggregated_holds AS (
    SELECT
        h.student_id,
        t.academic_year,
        MAX(CASE WHEN h.prevents_registration THEN 1 ELSE 0 END) AS has_blocking_hold,
        SUM(h.hold_amount) AS total_balance
    FROM registration_holds h
    JOIN term t ON h.term_id = t.term_id
    GROUP BY h.student_id, t.academic_year
)
SELECT
    cm.cohort,
    COALESCE(h.has_blocking_hold, 0) AS has_blocking_hold,
    COUNT(*) AS total_students,
    ROUND(AVG(CASE WHEN cm.retention THEN 1.0 ELSE 0.0 END), 4) AS retention_rate
FROM cohort_membership cm
LEFT JOIN pre_aggregated_holds h
    ON cm.student_id = h.student_id
    AND cm.cohort = h.academic_year
GROUP BY cm.cohort, COALESCE(h.has_blocking_hold, 0)
HAVING COUNT(*) >= 10;
```

## Why it works

1. Routing through `term` aligns the hold's `term_id` to the academic year represented by `cohort_membership.cohort`.
2. Grouping by `(student_id, academic_year)` reduces the cardinality to exactly 1 row per student per cohort year.
3. Using `MAX(...)` collapses multiple active holds into a single binary indicator (`has_blocking_hold`), maintaining exact cohort group counts.

## Prevention

Always inspect table grain before writing joins. Any table with a grain finer than `student` or `student_cohort` (such as `student_term_hold` or `student_term_course`) must be summarized before joining to entry cohort tables.
