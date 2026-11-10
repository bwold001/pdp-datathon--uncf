# Deploy student success chat

The Vercel project has three services: the Next.js frontend, the existing provider-free Results
API, and the dedicated chat service (`chat_app:app`). LiteLLM runs inside Python; no LiteLLM
proxy or additional account is required. Python 3.14 is selected by the root `.python-version`.

## What gets deployed

The Results and chat services both build `normalized-data-model/output/pdp.sqlite` using
`python -m api load` from the same committed synthetic inputs. Chat defaults to that bundled
extract through `DATABASE_URL`; reads are read-only and calculations are not cached. No database
is generated or modified during a request. Separate builds can have different load timestamps;
compare parameters, definitions and calculated values, not build timestamps or opaque source stamps.

`chat_app.py` gives only this dedicated service production defaults and a bundled SQLite URL.
It does not start the full Playground app, migrations, Workbench, document endpoints or uploads.
The full local Playground continues to use its configured database, including Workbench uploads.
Do not set a project-wide `DATABASE_URL` for this mock deployment: it would override chat's
bundled extract while the Results API still reads its own bundled extract. A shared external
database for the whole Explorer requires a separate coordinated change.

The first matching rewrite wins:

| URL | Service |
| --- | --- |
| `/api/v1/chat` | Chat |
| `/api/v1/uncf/chat` | Chat compatibility alias |
| `/api/v1/uncf/*` except chat | Existing Results and deterministic analysis API |
| Other paths | Next.js frontend |

The browser uses `/api/v1` as its base URL, so preview deployments call their own backend.
The old `/chat` and `/sandbox/data-chat-ui` pages still redirect to `/uncf/chat`.

## Configure Vercel

In the project dashboard, open **Settings → Environment Variables**. Set values separately for
Preview and Production; use a test key for Preview. Select the Secret type for provider keys.

| Name | Example | Type |
| --- | --- | --- |
| `UNCF_CHAT_MODEL` | `openai/gpt-4.1` or `anthropic/claude-sonnet-5-5` | Config |
| `OPENAI_API_KEY` | Your OpenAI API key, if OpenAI is selected | Secret |
| `ANTHROPIC_API_KEY` | Your Anthropic API key, if Anthropic is selected | Secret |
| `UNCF_CHAT_ENABLED` | `true` (dedicated service default) | Config |
| `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED` | `true` (Vercel build default) | Config |

Only the selected provider's key is used. Never put keys in `vercel.json`, source code, logs,
`NEXT_PUBLIC_*` variables, or screenshots. For local development use the ignored backend
`.env.development.local`. If a key is exposed, revoke it and replace it at the provider.

Model examples must be available to your provider account and support function/tool calling
through LiteLLM's `acompletion` interface. Other OpenAI or Anthropic model IDs can be configured,
but run the preview test before switching. Models requiring a different API need additional
integration work. There is no automatic fallback to another provider.

The default model preserves the existing Anthropic deployment setting, with an explicit
`anthropic/` prefix. Old unprefixed `claude-*` values acquire that prefix automatically.
Other provider prefixes are rejected with a configuration error until their credentials and
behavior have been added and tested.

Rebuild after changing frontend settings: Next.js embeds `NEXT_PUBLIC_*` values at build time.
The Vercel build command now honors an explicit `false` instead of overriding it. Configure
hosting duration to allow the included 120-second function limit. Chat has a 75-second
application deadline; each provider call has a 45-second timeout and no automatic retries.
The browser deadline remains 90 seconds. Calculation cancellation waits for database cleanup.

## Verify before production

1. Deploy a preview with the selected model and its test key. Check all three service builds.
2. Open `/uncf/chat`. Ask “What is the retention rate for all majors?” Select a cohort when asked.
3. Check that the full proposed scope appears before any calculation. Confirm it and inspect
   the receipt. This is synthetic demonstration data, not a finding about a campus.
4. Compare the receipt with `POST /api/v1/uncf/analyses` using the exact same parameters. The
   calculations, coverage and definitions should agree; build timestamps/source stamps may differ.
5. Check graduation and enrollment as well. Unknown or unavailable results must stay unknown;
   do not invent coverage declarations to make a demo produce numbers.
6. Verify missing-key (503), provider-error (502), invalid-input (422), unsupported-question,
   and timeout behavior. No error response should reveal provider exception details or keys.
7. Verify Explorer results, CSV exports, assets, and both old chat-page redirects still work.
8. Set the Production key/model, deploy, and repeat the live question on the production URL.

The automated suite uses scripted provider replies and independently counted fixtures. It proves
the adapter, confirmation flow, deterministic receipts and route wiring without spending provider
credits. It does not prove live model availability, provider credentials, or a successful Vercel
build; those require the preview checks above.

## Local checks

Root checks (use the root virtual environment with `requirements.txt` installed):

```bash
make check-fast
```

Playground checks (run from `playground/server_application`):

```bash
uv sync --locked
TEST_ON_SQLITE=true uv run pytest
uv run ruff check .
uv run ruff format --check .
```

To smoke-test the hosted entrypoint from the repository root, in a separate Python 3.14 virtual
environment, install `requirements-chat.txt`, run `python -m api load`, and then
`python -m uvicorn chat_app:app --port 8002`. Configure the model and key in that process's
environment. The hosted entrypoint does not read the local development secret file.

## Rollback

Set `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` and redeploy to hide the chat interface.
Set `UNCF_CHAT_ENABLED=false` to remove the backend routes too. Results and direct analysis routes
continue to use their existing service. The chat code never sends arbitrary SQL or executes a
calculation before explicit scope confirmation.
