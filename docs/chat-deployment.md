# Deploy student success chat

The Vercel project has three services: the Next.js frontend, the existing provider-free Results
API, and the dedicated chat service (`chat_app:app`). The official `openrouter==1.3.151` Python
SDK calls OpenRouter directly; an OpenRouter account and key are required. Python 3.14 is selected
by the root `.python-version`.

## What gets deployed

The Results and chat services both build `normalized-data-model/output/pdp.sqlite` using
`python -m api load` from the same committed synthetic inputs. Chat defaults to that bundled
extract through `DATABASE_URL`; reads are read-only and calculations are not cached. No database
is generated or modified during a request. After loading the extract, the chat build uninstalls
PyArrow, a build-only dependency unused by chat and deterministic calculations. This keeps the
function below Vercel’s bundle limit without changing the Results service or Playground dependencies. Separate builds can have different load timestamps;
compare parameters, definitions and calculated values, not build timestamps or opaque source stamps.

`chat_app.py` gives only this dedicated service production defaults and a bundled SQLite URL.
It does not start the full Playground app, migrations, Workbench, document endpoints or uploads.
The full local Playground continues to use its configured database, including Workbench uploads.
Do not set a project-wide `DATABASE_URL` for this mock deployment: it would override chat's
bundled extract while the Explorer API (`api/`) still reads its own bundled extract. A shared external
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
| `UNCF_CHAT_MODEL` | `openai/gpt-4.1` | Config |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Secret |
| `UNCF_CHAT_ENABLED` | `true` (dedicated service default) | Config |
| `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED` | `true` (Vercel build default) | Config |

One OpenRouter key supports changing the configured model. Never put keys in `vercel.json`,
source code, logs, `NEXT_PUBLIC_*` variables, or screenshots. For local development use the
ignored backend `.env.development.local`. If a key is exposed, revoke it and replace it at OpenRouter.

**Credential migration:** chat no longer reads `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
Set `OPENROUTER_API_KEY` separately in Preview and Production before deploying this version.
Use a canonical OpenRouter model ID, not a LiteLLM alias or a bare `claude-*` name. Existing
values are not mapped automatically. The default is `openai/gpt-4.1`; model availability,
account access, and tool support must be verified before changing it.

Check the configured ID against the live catalog before deployment (no key required):

```bash
export UNCF_CHAT_MODEL=openai/gpt-4.1
python - <<'PYTHON'
import json
import os
import urllib.request

with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=15) as response:
    models = json.load(response)["data"]
model_id = os.environ["UNCF_CHAT_MODEL"]
model = next((item for item in models if item["id"] == model_id), None)
if model is None or "tools" not in model.get("supported_parameters", []):
    raise SystemExit("Configured model is missing or does not advertise tool support")
print(model_id, "advertises tool support; verify account access in Preview next")
PYTHON
```

The catalog check does not establish account credit, endpoint availability, or correct tool use.
The live question checklist below verifies these with the configured Preview key.

Rebuild after changing frontend settings: Next.js embeds `NEXT_PUBLIC_*` values at build time.
The Vercel build command now honors an explicit `false` instead of overriding it. Configure
hosting duration to allow the included 120-second function limit. Chat has a 75-second
application deadline across all tool rounds; each provider call sets `timeout_ms=45000`,
`retries=None`, `stream=False`, and `max_completion_tokens=1500`. SDK retries are disabled.
OpenRouter may still route to backup providers within that single HTTP request.
The browser deadline remains 90 seconds. Calculation cancellation waits for database cleanup.

## Verify before production

1. Deploy a preview with the verified model and its OpenRouter test key. Check all three service
   builds and record the commit and Preview URL. The earlier deployment
   `dpl_7W9MhUNYG48ew5Nd4BXvRELkVWk2` failed with `LAMBDA_SIZE_EXCEEDED`: its chat bundle
   was 420.67 MB against a 225 MB limit. The logs showed LiteLLM and its dependency tree in the
   custom install. The first OpenRouter build shrank the bundle to 240.39 MB, still over the limit. The chat build
   now removes build-only PyArrow after loading the extract; verify the deployed bundle fits.
2. Open `/uncf/chat`. Ask “What is the retention rate for all majors?” Select a cohort when asked.
3. Check that the full proposed scope appears before any calculation. Confirm it and inspect
   the receipt. This is synthetic demonstration data, not a finding about a campus.
4. Compare the receipt with `POST /api/v1/uncf/analyses` using the exact same parameters. The
   calculations, coverage and definitions should agree; build timestamps/source stamps may differ.
5. Ask “What is the graduation rate for chemistry majors?” and “What is enrollment ethnicity
   by academic program over the past 2 years?” Resolve requested scope choices, confirm, and
   compare each receipt with direct analytics. Unknown or unavailable results must stay unknown;
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
make check
```

Playground checks (run from `playground/server_application`):

```bash
uv sync --locked
TEST_ON_SQLITE=true uv run pytest
uv run ruff check .
uv run ruff format --check .
```

To smoke-test the hosted entrypoint from the repository root, in a separate Python 3.14 virtual
environment, install `requirements-chat.txt`, run `python -m api load`, remove build-only PyArrow with
`python -m pip uninstall -y pyarrow`, and then
`python -m uvicorn chat_app:app --port 8002`. Configure the model and key in that process's
environment. The hosted entrypoint does not read the local development secret file.

## Rollback

Set `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` and redeploy to hide the chat interface.
Set `UNCF_CHAT_ENABLED=false` to remove the backend routes too. Results and direct analysis routes
continue to use their existing service. The chat code never sends arbitrary SQL or executes a
calculation before explicit scope confirmation.
