---
title: Trigger cancellation at the phase under test
date: 2026-11-23
category: test-failures
module: playground/server_application/tests
problem_type: test_failure
component: testing_framework
severity: medium
symptoms:
  - Cancellation tests returned a timeout before their calculation workers started in CI.
root_cause: timing_dependent_test
resolution_type: test_fix
tags: [squad-uncf, cancellation, sqlite, testing]
---

# Trigger cancellation at the phase under test

## Problem

Two cancellation tests limited the entire request to 50 milliseconds, including plan
validation and catalog construction. A slower runner could exhaust that budget before
the calculation started, failing assertions intended to verify worker cleanup.

## Solution

Expire the request's execution deadline after a real read begins. For SQL interruption,
expire it from a SQLite function while a bounded query is running and assert the underlying
SQLite interruption. Test validation expiry separately. Use events to hold worker cleanup
while checking that a cancelled asynchronous task remains pending until cleanup finishes.

## Why it works

Each test reaches the phase it intends to cancel without depending on machine speed.
Event waits have failure bounds but return immediately when signaled. No sleep or expensive
query is needed, and the production timeout and cancellation implementation stay unchanged.
