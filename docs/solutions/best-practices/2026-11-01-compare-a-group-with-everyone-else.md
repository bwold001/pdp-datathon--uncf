---
title: Comparing a group with everyone else without leaking hidden groups or overstating certainty
date: 2026-11-01
category: best-practices
module: gap_finder
problem_type: best_practice
component: data_model
severity: medium
tags: [squad-cca, gap-finder, suppression, privacy, confidence-intervals, newcombe]
---

# Comparing a group with everyone else without leaking hidden groups or overstating certainty

## Problem

When you compare a group with everyone minus that group, the comparison columns can give away a hidden
group's counts: if everyone else is under 10 students, everyone minus the shown group is the hidden group.
And the usual Wald interval (rate ± 1.96 standard errors) is wrongly narrow for small groups and for rates
near 0% or 100%. Any squad that builds its own group comparisons will hit both.

## What didn't work

- **Hiding only the group itself.** A group of 500 next to an everyone else of 3 still shows those 3
  students' counts in the comparison columns.
- **Rate ± 1.96 SE for each side.** For 0 of 12 against 50%, it gives −53.1 to −46.9 points: the group's
  own side has no width at all, since a rate of 0 has a standard error of 0.

## Solution

Use the gap finder (`find_gaps` or the `equity_gaps` table, see [gap_finder/README.md](../../../gap_finder/README.md))
rather than recomputing. In [gap_finder/compare.py](../../../gap_finder/compare.py):

- `gap_status` hides a group when the group or everyone else has fewer than 10 students.
- `newcombe_interval` combines a Wilson score interval for each side. For 0 of 12 against 50%, it gives
  −53.1 to −25.6 points.

## Why it works

Everyone else is everyone minus the group, so it needs the same size rule as the group. A Wilson
interval never collapses to zero width, so it stays honest at small sizes and at 0% or 100%.

## Prevention

- Tests in `gap_finder/tests/test_compare.py`: `test_hidden_when_everyone_else_is_under_ten` and
  `test_interval_is_honest_for_a_small_group_at_zero`.
- The `equity_gaps` table's CHECKs refuse a shown group under 10, and an `ok` row whose everyone else is
  under 10, even from code that skips `GapResult`.

## Known limit

These rules aren't enough on their own. When exactly one group in a breakdown is hidden for size, everyone
minus the shown groups still gives its counts by subtraction. The shared measures' `success_measures` table
has the same gap. It isn't fixed yet.

**The data is synthetic.** Nothing here is a finding about real students or institutions.
