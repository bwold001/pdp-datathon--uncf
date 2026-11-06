# Start your team's repo

At the hackathon, your team can work in its own repo copied from this one, or stay in this one.
Both work side by side.

**A copy is a snapshot.** Later fixes to this starter don't reach your copy, so check
[the starter's commit history](https://github.com/devcolor/pdp-datathon-starter/commits/main) for
changes if something here looks out of date.

## Make your own copy

1. Create the repo (or click **Use this template** on GitHub):

   ```bash
   gh repo create <org>/<name> --template devcolor/pdp-datathon-starter --private --clone
   cd <name>
   ```

2. Install the Python packages and run the checks. See [Python packages](../README.md#python-packages):

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   python -m pip install -r requirements.txt
   make check
   ```

3. If your team uses GitHub Issues, copy the labels. A template copy doesn't bring them:

   ```bash
   gh label clone devcolor/pdp-datathon-starter
   ```

4. Pick your issue tracker. [`docs/agents/issue-tracker.md`](agents/issue-tracker.md) tells agents
   where issues live, and the "Agent skills" section of [`AGENTS.md`](../AGENTS.md) points to it.
   - **GitHub Issues:** remove the proposal and `squad:*` conventions.
   - **Another tracker:** rewrite the file for that tracker.
   - **No tracker:** delete the file and its section in `AGENTS.md`. The
     [workflow](../README.md#which-skill-when) doesn't need one.

5. Remove the proposal process, which belongs to this shared repo:
   - `.github/ISSUE_TEMPLATE/foundation-proposal.md`
   - "Submit a proposal" and "Deliver funded work" in `README.md`
   - The proposal rules in `CONTRIBUTING.md`, the pull request template, and `AGENTS.md`

6. Turn on branch protection if you want it. A copy doesn't bring this repo's required checks. To
   match this repo, make `data` and `links` required on `main`.

### Keep or delete the foundations

Keep what you'll use. If you delete one, remove what runs it too, or your checks will fail:

| To delete | Also remove |
| --- | --- |
| `normalized-data-model/` | Its line under `check:` in the [`Makefile`](../Makefile), the `postgres` service and `PDP_*` settings in [`check.yml`](../.github/workflows/check.yml), its row in the README's "Foundations" table, its command in the README's "Checks" section, its entry under "Never commit generated outputs" in `AGENTS.md`, and its paths in `.gitignore` |
| `playground/` | The `playground` job in `check.yml`, and the "dev/color Playground" section in the README |

When your copy is set up, delete this file and the README's pointer to it. It links to both
foundations, so deleting one breaks the `links` check until this file is gone too.

If your team only wants the Playground, follow
[its own setup](../playground/README.md#how-to-create-a-playground-for-your-organization) instead.

Keep `data/raw/` and `scripts/check.py` unless your team replaces the data. The README's
[Checks](../README.md#checks) section explains how to change the data on purpose. The data stays
synthetic in your copy, so nothing built on it is a finding about real students or institutions.

## Stay in this repo

- Name your branches `team/<name>/...`.
- Change your own team's files freely on those branches.
- Change shared foundation files only through a pull request. See
  [CONTRIBUTING.md](../CONTRIBUTING.md).
