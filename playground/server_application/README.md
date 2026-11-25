# Server Application

The FastAPI back end for the Student Persistence and Pathway Explorer. It serves the
[Client Application](../client_application/README.md). The data is synthetic.

## Layout

```
app/
├── main.py               # create_app(): CORS, error handlers, the Explorer router and chat
├── uncf.py               # Mounts the Explorer API from the repo's top-level api/ (/api/v1/uncf/...)
├── core/config.py        # Settings, resolved from APP_ENV
├── core/errors.py        # One JSON shape for every error
├── chat/                 # The bounded chat: provider calls, validated tools, routes
└── services/analytics.py # Read-only snapshots of DATABASE_URL for the chat's analyses
tests/
```

Calculations don't live here: the Explorer's numbers come from `measures/` and `api/`, and the
chat's from `analytics/`, at the repo root.

## Run it

`mise run api:dev` from `playground/`, after the root README's
[quick start](../../README.md#quick-start-on-the-mock-data) steps. Health check:
http://localhost:8000/api/v1/uncf/health

## Settings

`APP_ENV` (development, staging or production) picks the committed `.env.<APP_ENV>` file. Put
secrets and personal overrides in `.env.<APP_ENV>.local`, which git ignores. Every variable is in
[.env.example](.env.example) and the [integration guide](../../docs/integration.md#4-settings).

## Chat

`POST /api/v1/chat` serves the bounded graduation, retention and enrollment assistant.
`/api/v1/uncf/chat` is an alias with the same handler and typed receipt contract.

- `app/chat/` holds only orchestration, tools and transport. Every number it shows comes from a
  validated receipt from `analytics/`, never from model-written text.
- `app/services/analytics.py` reads `DATABASE_URL` read-only. There is no fallback to another
  extract or a cached result, and errors don't expose credentials.
- Coverage declarations come from `UNCF_ANALYTICS_CONFIG` or `analytics/config/analytics.yaml`.
- The [dedicated Vercel chat service](../../docs/chat-deployment.md) uses the same adapter with a
  build-generated mock extract and mounts only the chat routes.

## Tests

```bash
mise run api:lint
mise run api:test
```

The tests build their own small SQLite files. The Postgres parity tests run only when
`PDP_TEST_POSTGRES_URL` is set; `PDP_REQUIRE_POSTGRES=1` makes a skip fail, as CI does.
