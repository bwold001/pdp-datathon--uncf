---
title: Keep legacy chat redirects ahead of the production Sandbox guard
date: 2026-11-10
category: integration-issues
module: playground/client_application
problem_type: integration_issue
component: deployment
severity: medium
symptoms:
  - The canonical chat page loads but an old Sandbox chat bookmark returns 404 in production.
root_cause: route_guard_order
resolution_type: code_fix
tags: [squad-uncf, chat, nextjs, deployment]
---

# Keep legacy chat redirects ahead of the production Sandbox guard

## Problem

The redirect inside `/sandbox/data-chat-ui/page.tsx` cannot preserve production bookmarks:
its parent Sandbox layout calls `notFound()` when Sandbox is disabled. Development checks
miss this because Sandbox is enabled there.

## Solution

Declare `/sandbox/data-chat-ui` → `/uncf/chat` in `next.config.ts`'s `redirects()`.
Next.js checks this redirect before resolving page layouts. The other Sandbox pages stay disabled.

## Prevention

Build with production settings, start that build, and request the old URL directly. Follow the
redirect and verify the enabled chat page. Check `/sandbox` still returns 404. A passing
development story does not exercise the production layout guard.
