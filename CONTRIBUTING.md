# Contributing

How the UNCF squad (Beza, Daryl, Fuad, Stella) gets changes into `main`. Nobody pushes to `main`;
branch protection requires a pull request, one approval, and passing checks.

## Before you start

1. Look at the project board.
2. Pull the latest `main`.
3. Claim a task and name a reviewer on the board. Confirm its acceptance criteria.
4. If your change touches a shared file or the result contract, tell the squad **before** you
   build it.

## Build and open a pull request

1. Branch from `main` with a short-lived branch, such as `daryl/retention-measure`.
2. Make focused commits. Open a draft pull request early. The template fills in.
3. Link the task: `Closes #N`, or `Refs #N` if more pull requests are coming.
4. Run the checks from the README's [Checks](README.md#checks) section. Foundations and the
   Playground are checked separately.
5. Ask a teammate to review. Merge after approval and passing checks.
6. Keep `main` runnable. Unfinished stretch work stays disabled or on a branch.

## What the reviewer checks

- The acceptance criteria in the task are met, and the validation steps were run.
- Numbers match the shared measures; every nonempty small group remains visible.
- Anything others use is explained in a README.
- Changes to shared files or the result contract were announced.

## Check-out note

At the end of a session, post: task or PR · working now · remaining · checks run · blocker or
decision needed · next action and owner.
