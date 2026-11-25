---
title: Preserve unavailable-result explanations through receipt adapters
date: 2026-11-23
category: ui-bugs
module: analytics
problem_type: ui_bug
component: chat
severity: medium
symptoms:
  - Graduation scope confirmation produced an unexplained table of unavailable results.
root_cause: lost_metadata
resolution_type: code_fix
tags: [squad-uncf, chat, receipts, missing-evidence]
---

# Preserve unavailable-result explanations through receipt adapters

## Problem

The graduation owner distinguished observation horizons and supplied limitation
notes. The chat adapter reduced unavailable rows to their status, dropping the
perspective, horizon and explanation. Users could mistake missing evidence for no
graduates.

## Solution

Preserve bounded nonnumerical explanation metadata on unavailable receipt rows.
Assign explicit reasons in analytical owners, then generate presentation text only
from disclosed receipts. Explain unverified coverage separately from insufficient
declared follow-up. Never infer an empty population from a missing denominator.

## Prevention

The exact Chemistry-family question is exercised through HTTP confirmation,
execution and replay. Independent tests distinguish known empty populations from
unknown eligibility and preserve valid zero rates for groups of one through nine.
Catalog suggestions also distinguish schema support from actual outcome availability.
