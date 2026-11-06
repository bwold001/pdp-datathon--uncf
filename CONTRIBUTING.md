# Contributing

Six squads build on this repo. These rules keep every pull request reviewed the same way.

## Before you start

Work here starts from a funded proposal. If you don't have one yet, see
[Submit a proposal](README.md#submit-a-proposal). The proposal's DRI builds it, and its Reviewer
(from a different squad) tests it.

## Build and open a pull request

1. Branch from `main`. Use one pull request per proposal when you can. A bigger proposal can land
   as several smaller pull requests.
2. Open a pull request. The template fills in automatically.
3. Link the pull request to its proposal in the description:
   - **One pull request, or the last of several:** write `Closes #<proposal issue>`. This closes
     the issue when it merges.
   - **An earlier pull request of several:** write `Refs #<proposal issue>`. This links it
     without closing the issue.
4. Ask the proposal's Reviewer to review.

## What the Reviewer checks

The Reviewer works through the checklist in the pull request template:

- The description says `Closes #<proposal issue>`, or `Refs #<proposal issue>` if more pull
  requests are coming for that proposal.
- The Reviewer ran the proposal's completion test, and it passed.
- If this adds something other squads will use, the README explains how to use it.

When every box is checked, the Reviewer approves. A pull request needs one approval before it can
merge into `main`.

## If it grows

If the work needs more hours or more scope than the Leads approved, stop and ask the Leads in the
proposal issue before spending more.
