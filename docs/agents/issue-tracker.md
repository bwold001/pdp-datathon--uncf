# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in `bwold001/pdp-datathon--uncf`. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Repo-specific conventions

- Tasks use the `.github/ISSUE_TEMPLATE/task.md` template: one owner, one reviewer, acceptance criteria, validation, and a priority (Core / Stretch 1 / Stretch 2).
- Pull requests link their task with `Closes #N`, or `Refs #N` if more pull requests are coming. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
