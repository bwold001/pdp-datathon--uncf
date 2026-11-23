# Playground

The web app for the Student Success Explorer: a Next.js client and a FastAPI server. All data is
synthetic: nothing here describes real students or institutions.

- [`client_application/`](client_application/README.md): the Explorer pages (`/uncf/paths`, `/uncf/dfw`,
  `/uncf/gateway`, `/uncf/credit-momentum`) and the chat page (`/uncf/chat`). `/` redirects to
  `/uncf/paths`.
- [`server_application/`](server_application/README.md): mounts the Explorer API from the repo's
  top-level [`api/`](../api/) under `/api/v1/uncf`, and the chat at `/api/v1/chat`.

Both read one SQLite file, `normalized-data-model/output/pdp.sqlite`, built from the mock PDP files
in `data/raw/`. No database server or Docker is needed.

## Run it

You need [mise](https://mise.jdx.dev). It installs the pinned bun, Node, Python and uv versions.

```bash
cd playground
mise trust && mise install
mise run api:install     # backend dependencies
mise run api:load        # build normalized-data-model/output/pdp.sqlite (once, or after data changes)
mise run api:dev         # API on http://localhost:8000 (docs at /docs)
```

In a second terminal:

```bash
cd playground
mise run web:install
mise run web:dev         # Explorer on http://localhost:3000
```

The chat needs an [OpenRouter](https://openrouter.ai) key. Put it in
`server_application/.env.development.local` (git-ignored), never in a committed file:

```bash
OPENROUTER_API_KEY=<your key>
```

Without a key the Explorer tabs work and the chat answers with a "missing key" message.

## Checks

| Command | What it checks |
|---|---|
| `mise run api:lint` | Ruff lint and format on the server |
| `mise run api:test` | Server tests (Postgres parity tests skip unless `PDP_TEST_POSTGRES_URL` is set) |
| `mise run web:build` | Production build; run it before `web:lint`, which needs its generated types |
| `mise run web:lint` | ESLint and the TypeScript check |
| `mise run web:test-storybook` | The Explorer's Storybook stories and their play functions, in Chromium |

`mise tasks` lists every command. CI runs all of these except `web:test-storybook`.

## Windows

mise runs task commands with `cmd` on Windows. If a task fails there, run it from Git Bash, or run
the command it wraps directly (for example `uv run fastapi dev app/main.py` in
`server_application/`).
