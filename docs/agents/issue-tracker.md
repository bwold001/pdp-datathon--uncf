# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in `devcolor/pdp-datathon-starter`. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Repo-specific conventions

- Squad proposals use the `proposal` label, plus `funded` / `not-funded`, `squad:*`, and `feedback_given`. These belong to the proposal process — don't add or remove them as part of triage.
- Pull requests link their issue with `Closes #N`, or `Refs #N` if more pull requests are coming. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Tickets broken out of a funded proposal put `Refs #<proposal>` in the body. A pull request that finishes a ticket still writes `Closes #<proposal>` (or `Refs #<proposal>` if more are coming), never `Closes #<ticket>`, so the Reviewer's checklist and the proposal issue keep working.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
