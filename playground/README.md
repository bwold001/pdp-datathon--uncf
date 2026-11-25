# Playground

The web app for the Student Persistence and Pathway Explorer: a Next.js client and a FastAPI server. All data is
synthetic: nothing here describes real students or institutions.

- [`client_application/`](client_application/README.md): the Explorer pages (`/uncf/paths`, `/uncf/dfw`,
  `/uncf/gateway`, `/uncf/credit-momentum`) and the chat page (`/uncf/chat`). `/` redirects to
  `/uncf/paths`.
- [`server_application/`](server_application/README.md): mounts the Explorer API from the repo's
  top-level [`api/`](../api/) under `/api/v1/uncf`, and the chat at `/api/v1/chat`.

Both read one SQLite file, `normalized-data-model/output/pdp.sqlite`, built from the mock PDP files
in `data/raw/`. No database server or Docker is needed.

## Run it

Setup and the two commands that start it are in the root README's
[quick start](../README.md#quick-start-on-the-mock-data). `mise tasks` lists every command.

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

See [known issues](../docs/known-issues.md#setup).
