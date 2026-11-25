# Integration guide: running the Student Persistence and Pathway Explorer on your own PDP data

For the IT and institutional research staff at Florida Memorial University (FMU) and Benedict College
who will run the Explorer after handoff. It covers how the app gets its data, how to load your own PDP
files, where to host it, how to require sign in, how to turn chat off or point it at your own AI
service, and what to check before real student data goes in.

Everything in this repo was built and tested on **synthetic mock data**. No number it shows today is a
finding about real students or either school.

## Contents

1. [How it works](#1-how-it-works)
2. [What you need](#2-what-you-need)
3. [Load your data](#3-load-your-data)
4. [Settings](#4-settings)
5. [Tell the app about your data](#5-tell-the-app-about-your-data)
6. [Hosting](#6-hosting)
7. [Sign in and access](#7-sign-in-and-access)
8. [Chat](#8-chat)
9. [Getting numbers into Power BI or a data lake](#9-getting-numbers-into-power-bi-or-a-data-lake)
10. [Before real data goes in](#10-before-real-data-goes-in)
11. [Known limits and open items](#11-known-limits-and-open-items)
12. [Notes for developers who extend it](#12-notes-for-developers-who-extend-it)

## 1. How it works

1. **Your PDP files.** You download your two PDP analysis ready files, the cohort file and the course
   file, from the National Student Clearinghouse. The app never connects to your student information
   system.
2. **The load.** `python -m api load` hands both files to the loader in `normalized-data-model/`. It
   checks every row against the PDP data dictionary, holds back rows that break a rule, and builds clean
   tables: students, cohorts, terms, courses and enrollments.
3. **One database file.** The tables go into one SQLite file (`normalized-data-model/output/pdp.sqlite`,
   or wherever `UNCF_DATABASE` says). The sample is about 24 MB for 10,313 students.
4. **Live answers.** Each time someone opens a page, exports a PDF or asks the chat, the measures run SQL
   on that file. Nothing is precomputed, and nothing is written back to the file or to your systems.

The app has three parts:

| Part | What it is | Runs on |
| --- | --- | --- |
| **Explorer pages** | The Next.js web app staff use, with PDF export | Node 24 and bun to build, Node to run |
| **API** | `api/`: every number, as JSON or CSV, under `/api/v1/uncf` | Python 3.10 or newer |
| **Chat** (optional) | `chat_app.py`: the bounded chat, which calls an AI model | Python 3.14 |

A web server in front sends each address to the right part. On Vercel, `vercel.json` does this.

## 2. What you need

- **Your two PDP files** (cohort and course), as CSV. Their column names must match the ones the loader
  expects (see [section 10](#10-before-real-data-goes-in)).
- **Somewhere to run it:** your own Linux server or cloud account, or a Vercel team (see
  [section 6](#6-hosting)).
- **A person who can run a few commands** for the first load and for each new release of PDP files. No
  database administrator is needed.
- **Your sign in system**, such as Microsoft Entra ID, if access should follow your staff accounts.

## 3. Load your data

### Option A: files on the server (recommended)

Copy the two files to the server, then from the repo root, with the Python environment active:

```bash
python -m api load --cohort /secure/pdp/cohort_2026.csv --course /secure/pdp/course_2026.csv
```

- It always rebuilds the database from the files you name.
- Set `UNCF_DATA_LABEL=institution` and `UNCF_SOURCE` for the API and chat (section 4), so every page,
  answer and receipt says the numbers come from your files, not the synthetic sample.
- It uses `api/config/school_pipeline.yaml`: your cohort and course files only. The sample's two extra
  files (synthetic housing and another school's calendar) are left out.
- At the end it prints how many rows were read, passed and held back. Held back rows are listed in
  `normalized-data-model/logs/failed_records/`, with the rule each one broke.
- The sample load takes under a minute.

### Option B: private links (for hosted builds)

A hosted build such as Vercel can't take command line arguments. Set two secret settings instead, each an
`https` link to the file in private storage (for example an Azure Blob link with a read only, time limited
token):

```bash
UNCF_COHORT_URL=https://...   UNCF_COURSE_URL=https://...   python -m api load
```

The links are never written to the log, only the storage host. Plain `http` links are refused.

### Loading new files

When NSC sends a new release, run the same load command again. The API notices the new file and drops
its cached answers, so it doesn't need a restart. Restart it only after changing a setting.

### Other databases

| Database | Loader | Explorer pages and API | Chat |
| --- | --- | --- | --- |
| **SQLite** (default) | Yes | Yes | Yes |
| **PostgreSQL** | Yes (`--backend postgres`, `PDP_POSTGRES_URL`) | No | Yes (`DATABASE_URL`) |
| **SQL Server, Azure Data Lake** | No | No | No |

Use SQLite. It is one file, needs no database server, and is plenty for a college's PDP files. Reading
from SQL Server directly would need a SQL Server option in the loader and the read layer; the measure SQL
is mostly standard, so it is a contained project, but it isn't built.

### What a load leaves on disk

A load keeps working copies that hold student level rows: `normalized-data-model/data/staging/<run id>/`,
`normalized-data-model/output/tables/` and `normalized-data-model/logs/failed_records/`. On real data,
keep the whole folder readable only by the account that runs the app, and delete old runs under
`data/staging/` once a load is checked. The PDP files themselves should live outside the repo, never in
git.

## 4. Settings

Set these as environment variables (on Vercel, in the project's settings).

**Data and API**

| Setting | Default | What it does |
| --- | --- | --- |
| `UNCF_DATABASE` | `normalized-data-model/output/pdp.sqlite` | The SQLite file the load writes and the API and chat read |
| `UNCF_COHORT_URL`, `UNCF_COURSE_URL` | none | `https` links to your two files, for a build that can't pass `--cohort` and `--course` |
| `UNCF_DATA_LABEL` | `synthetic` | What kind of data is loaded: `synthetic` (the sample) or `institution` (your own PDP files). The Explorer's badge, page notes and shared PDFs, the chat's cards and instructions, and every answer and receipt follow it. Set `institution` whenever you load your own files |
| `UNCF_SOURCE` | "PDP analysis-ready cohort and course files (synthetic sample)" | The source every answer names, for example "FMU PDP files, fall 2026 release" |
| `UNCF_ANALYTICS_CONFIG` | `analytics/config/analytics.yaml` | What you know about your data's coverage (see [section 5](#5-tell-the-app-about-your-data)) |
| `UNCF_SCHOOL` | none | `fmu` or `benedict`: show metrics under the school's own names (see section 5) |
| `UNCF_CORS_ORIGINS` | `http://localhost:3000` | Other web addresses allowed to call the API from a browser. Not needed when the pages and API share one address |
| `UNCF_ANALYSIS_V2_TIMEOUT_SECONDS` | 10 | How long one chat calculation may run |

**Chat**

| Setting | Default | What it does |
| --- | --- | --- |
| `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED` | on (Vercel) | `false` hides chat in the pages. Read when the pages are built, so rebuild after changing it |
| `UNCF_CHAT_ENABLED` | off locally, on in `chat_app.py` | `false` stops the chat service from answering |
| `OPENROUTER_API_KEY` | none | The key for the AI model service (see [section 8](#8-chat)) |
| `UNCF_CHAT_MODEL` | `openai/gpt-4.1` | Which model the chat uses |
| `DATABASE_URL` | the SQLite file above | What the chat reads, if not the SQLite file |

Cohort years are not a setting: the API offers the years in your loaded data.

## 5. Tell the app about your data

Copy `analytics/config/analytics.yaml`, fill it in, and point `UNCF_ANALYTICS_CONFIG` at your copy.

- `provisional_retention_cohorts`: classes whose second year isn't fully in your files yet. The pages
  mark their year 2 numbers as provisional, and the default class shown is the latest one not listed.
- `complete_academic_years`, `cohort_followup_years` and `cutoff`: confirm these with your institutional
  research office before the chat reports graduation or annual enrollment. Until then those answers say
  the information is unavailable, by design.

Other choices to make on your first real load:

- **Fixes for the mock data.** `normalized-data-model/config/data_fixes.yaml` corrects known bugs in the
  mock files, such as race labels cut at 25 characters and program codes that lost a leading zero. Review
  each against your real files. Each has an `enabled` switch; to change them, copy the file and name your
  copy as `fixes` in `api/config/school_pipeline.yaml`.
- **Your own metric names.** With `UNCF_SCHOOL` set, the pages show the names in `LOCAL_NAMES` in
  `measures/definitions.py` (empty today) and keep the PDP name alongside.

## 6. Hosting

Two paths. Both run the same code.

### Path A: Vercel (fastest, for a pilot or the mock data)

The repo already deploys to Vercel as is (`vercel.json`).

1. Create your own Vercel team. The free Hobby plan is for personal use, so an institution needs Pro.
2. Copy the repo into your GitHub organization and import it into the team as a new project.
3. Set the settings from [section 4](#4-settings) in the project. To start without chat, set
   `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` and `UNCF_CHAT_ENABLED=false`.
4. Turn on deployment protection (see [section 7](#7-sign-in-and-access)), then deploy.

With no file settings, each deploy builds the database from the mock files in `data/raw/`. For real
data, set `UNCF_COHORT_URL` and `UNCF_COURSE_URL` to private links (section 3, option B) and redeploy;
each deploy downloads the files and rebuilds. The built database then sits in Vercel's cloud, so your
data governance office must approve that first.

### Path B: your own server (recommended for real data)

**One time setup** on a Linux server (Ubuntu or similar):

```bash
# 1. Code and Python environment (Python 3.10 or newer)
git clone <your copy of the repo> /opt/student-success && cd /opt/student-success
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt

# 2. Your data
.venv/bin/python -m api load --cohort /secure/pdp/cohort.csv --course /secure/pdp/course.csv

# 3. The pages (Node 24 and bun; this step can also run on another machine and be copied over)
cd playground/client_application
bun install --frozen-lockfile
NEXT_PUBLIC_API_BASE_URL=/api/v1 NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false bun run build
```

**Run the API and the pages as services** that start with the server. Example systemd units:

```ini
# /etc/systemd/system/explorer-api.service
[Service]
User=explorer
WorkingDirectory=/opt/student-success
EnvironmentFile=/etc/student-success.env
ExecStart=/opt/student-success/.venv/bin/python -m api serve --host 127.0.0.1 --port 8001
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/explorer-pages.service
[Service]
User=explorer
WorkingDirectory=/opt/student-success/playground/client_application
# Listen on the server itself only: next start alone listens on every address, which would let people
# reach the pages on port 3000 without going through nginx and sign in.
ExecStart=/opt/student-success/playground/client_application/node_modules/.bin/next start --hostname 127.0.0.1 --port 3000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`/etc/student-success.env` holds the settings from section 4, one `NAME=value` per line. If chat runs,
start it the same way on `127.0.0.1` port 8002. Every part listens on `127.0.0.1` only, so nginx is the one
way in.

**Route addresses with nginx,** the same way `vercel.json` does:

```nginx
server {
    listen 443 ssl;
    server_name explorer.example.edu;            # your address and certificate
    ssl_certificate     /etc/ssl/explorer.crt;
    ssl_certificate_key /etc/ssl/explorer.key;

    location /api/v1/uncf/chat { proxy_pass http://127.0.0.1:8002; }   # only if chat runs
    location /api/v1/chat      { proxy_pass http://127.0.0.1:8002; }   # only if chat runs
    location /api/v1/uncf/     { proxy_pass http://127.0.0.1:8001; }
    location /                 { proxy_pass http://127.0.0.1:3000; }
}
```

Check it: `https://<your address>/api/v1/uncf/health` should say `"data_available": true`, and the home
page should open the Student paths page.

### What this looks like at each school

**FMU (Linux server, Microsoft SQL Server, Power BI)**
- Path B on the existing Linux server. No database server is needed: the app keeps its own SQLite file.
- The institutional research office provides the PDP files; whoever runs the server loads them (section 3, option A).
- Keep it on the campus network, with sign in in front (section 7).
- Start with chat off. FMU requires any AI model to run on its own servers (section 8).
- Power BI reads the API's CSV output (section 9).

**Benedict (Azure, Azure Data Lake, Power BI, Entra ID)**
- Path B on an Azure Linux virtual machine, with Entra ID sign in in front (section 7).
- Load the PDP files from Azure Blob Storage with private links (section 3, option B) or copy them to the
  machine.
- The weekly Data Lake batch can fetch the API's CSV output (section 9). Confirm the columns against the
  Data Lake's schema first.
- Chat can use Azure OpenAI once the model provider is switched (section 8).

A ready made container image would let Benedict run the same thing on Azure App Service, and make Path B
a single command everywhere. It is a planned follow up, not built yet.

## 7. Sign in and access

The app has no sign in of its own. Anyone who can reach its address sees everything, so put sign in in
front of it. That covers the pages, the API and the chat together, with no code change.

**Make nginx the only way in.** Sign in at nginx protects nothing if people can reach the app another way:

1. Every part listens on `127.0.0.1` only (section 6): the API with `--host 127.0.0.1`, the pages with
   `next start --hostname 127.0.0.1`, and chat, if it runs, the same way.
2. The server's firewall allows only HTTPS (port 443) from users, plus whatever your IT staff use to
   administer it. For example, with ufw: `ufw default deny incoming`, `ufw allow 443/tcp`, then your
   administration rule, then `ufw enable`.
3. nginx checks sign in on **every** address it serves, not only the home page (below).
4. Check from another machine: `https://<your address>/api/v1/uncf/health` and
   `http://<server>:3000` and `:8001` should all fail or ask you to sign in.

**With Microsoft Entra ID (Benedict, and FMU if it uses Microsoft 365)**
1. Run [oauth2-proxy](https://oauth2-proxy.github.io/oauth2-proxy/) on the same server, set up with its
   Microsoft Entra ID provider, listening on `127.0.0.1:4180` in reverse proxy mode
   (`--http-address=127.0.0.1:4180 --reverse-proxy=true --upstream=static://202`).
2. Have nginx ask it before every request. In the `server` block from section 6:

   ```nginx
   # oauth2-proxy's own sign in pages.
   location /oauth2/ {
       proxy_pass http://127.0.0.1:4180;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Auth-Request-Redirect $request_uri;
   }
   # The check nginx runs for every request below.
   location = /oauth2/auth {
       internal;
       proxy_pass http://127.0.0.1:4180;
       proxy_set_header Host $host;
       proxy_set_header Content-Length "";
       proxy_pass_request_body off;
   }

   # The app: each location checks sign in first, and sends anyone not signed in to sign in.
   location /api/v1/uncf/chat { auth_request /oauth2/auth; error_page 401 = /oauth2/sign_in; proxy_pass http://127.0.0.1:8002; }
   location /api/v1/chat      { auth_request /oauth2/auth; error_page 401 = /oauth2/sign_in; proxy_pass http://127.0.0.1:8002; }
   location /api/v1/uncf/     { auth_request /oauth2/auth; error_page 401 = /oauth2/sign_in; proxy_pass http://127.0.0.1:8001; }
   location /                 { auth_request /oauth2/auth; error_page 401 = /oauth2/sign_in; proxy_pass http://127.0.0.1:3000; }
   ```

   A location without `auth_request` is open to anyone, so add it to any location you add later.
3. In the Microsoft Entra admin center, open the app under Enterprise apps, set **Assignment required?**
   to **Yes**, and add the faculty or a group under **Users and groups**. Only they can sign in; adding a
   person to the group gives access later. ([Microsoft's steps](https://learn.microsoft.com/entra/identity-platform/howto-restrict-your-app-to-a-set-of-users))

Azure App Service's built in authentication does the same job without oauth2-proxy, once the container
image exists (section 6).

**Without Entra ID:** keep the server on the campus network or VPN only, and add a password for each
person at nginx (`auth_basic` and `auth_basic_user_file` in the `server` block, so every location
inherits it), over HTTPS only. Fine for a small first group.

**On Vercel** ([plans and prices](https://vercel.com/docs/deployment-protection/usage-and-pricing)):
- **Vercel Authentication:** only members of your Vercel team get in, so each person needs a seat.
- **Password Protection:** one shared password, $20 per project per month on Pro.
- **Trusted IPs** (campus network only): Enterprise plan only.

None of the Vercel options uses your school's own accounts, which is another reason to prefer Path B for
real data.

## 8. Chat

### Turn chat off

- **On Vercel:** set `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` and `UNCF_CHAT_ENABLED=false`, then
  redeploy. Both default to on there.
- **On your own server:** build the pages with `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` and don't
  run the chat service.

The Explorer pages, PDF export and the API keep working with chat off.

### How chat uses an AI model

The model never calculates. It turns a question into a plan, staff confirm it, and every number comes from
the same calculations the pages use, with a receipt ([how the chat works](chat.md)). Today the chat calls
models through OpenRouter, a cloud service, with `OPENROUTER_API_KEY` and `UNCF_CHAT_MODEL`. You need
your own OpenRouter account, and you pay for its use. The question text goes to OpenRouter and the model
you pick, so check their terms (do they store inputs or train on them?) first.

Use a model that supports tool calls, written as OpenRouter's `provider/model` ID (default
`openai/gpt-4.1`). To check that a model exists and advertises tool support, with no key needed:

```bash
curl -s https://openrouter.ai/api/v1/models | python -c "import json,sys; m={x['id']:x for x in json.load(sys.stdin)['data']}.get('openai/gpt-4.1'); print('ok' if m and 'tools' in m.get('supported_parameters',[]) else 'missing or no tool support')"
```

That doesn't prove your account can use it, or that it calls tools well: the
[model check](chat.md#check-a-model-before-you-rely-on-it) does.

### Run chat on your own server

Chat runs as its own small service, `chat_app.py`, next to the API and the pages (section 6). In a
separate Python 3.14 environment, from the repo root:

```bash
python3.14 -m venv .venv-chat && .venv-chat/bin/python -m pip install -r requirements-chat.txt
.venv-chat/bin/python -m api load            # or point DATABASE_URL at the database the API uses
OPENROUTER_API_KEY=... UNCF_CHAT_MODEL=openai/gpt-4.1   .venv-chat/bin/python -m uvicorn chat_app:app --host 127.0.0.1 --port 8002
```

Put the key in the service's environment file, not in the repo. `chat_app.py` doesn't read the
Playground's `.env.development.local`. nginx sends `/api/v1/chat` and `/api/v1/uncf/chat` to it
(section 6). For local development, the Playground server (`mise run api:dev`) serves chat itself.

### Chat on Vercel

`vercel.json` deploys chat as a third service and turns it on. In the project's **Settings →
Environment Variables**, set these separately for Preview and Production (use a test key for Preview):

| Name | Example | Type |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | your OpenRouter key | Secret |
| `UNCF_CHAT_MODEL` | `openai/gpt-4.1` | Plain |
| `UNCF_CHAT_ENABLED` | `true` | Plain |
| `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED` | `true` | Plain |

Never put a key in `vercel.json`, code, logs, a `NEXT_PUBLIC_*` variable or a screenshot. If one is
exposed, revoke it at OpenRouter and set a new one. Rebuild after changing a `NEXT_PUBLIC_*` setting:
the pages read them when they're built. Allow functions to run for 120 seconds: an answer can take up to
75. Don't set a project-wide `DATABASE_URL`: chat and the API each build and read their own copy of the
database during the deploy.

### Check chat before staff use it

1. Run the [model check](chat.md#check-a-model-before-you-rely-on-it) with the model and key you'll use.
2. Open `/uncf/chat` and ask "What is the retention rate for all majors?" Pick a cohort when asked.
   The full plan should appear before anything is calculated. Confirm it and open the receipt.
3. Send the same confirmed plan to `POST /api/v1/uncf/analysis-v2/execute` (see
   [the analysis API](chat.md#using-the-analysis-api-without-chat)). The numbers, definitions and data
   references should match the chat's receipt.
4. Ask "What is the graduation rate for chemistry majors?" and "What is enrollment ethnicity by
   academic program over the past 2 years?" Unknown or unavailable answers must stay that way until
   your data's coverage is declared (section 5). Don't declare coverage just to make numbers appear.
5. Try a question the chat shouldn't answer, such as "Why do students leave?", and check that it says
   so. Turn the key off and check that chat shows a configuration message, with no error details.
6. Check that the pages and their PDF and CSV exports still work.

### Roll back

Turning chat off (above) is the fastest way back, and leaves the pages working. To return to an earlier
version, redeploy the last version you checked, for the pages, the API and chat together, and repeat
step 2. Don't reload the database while an answer is running.

### Using your own AI service

Azure OpenAI, OpenRouter, and model servers you run yourself (such as vLLM or Ollama) all accept the same
OpenAI style requests. Microsoft documents that the standard OpenAI client works with Azure OpenAI by
setting its address to `https://<your resource>.openai.azure.com/openai/v1/`
([Microsoft's page](https://learn.microsoft.com/azure/ai-foundry/openai/api-version-lifecycle)).

So switching services is a contained change to one class,
`playground/server_application/app/chat/provider.py`, driven by three settings: the service's
address, its key and the model or deployment name. It is planned, not built: until then, chat works
only with OpenRouter.

Whatever service you choose, test it with the chat's own questions first: the chat depends on the model
calling tools correctly.

## 9. Getting numbers into Power BI or a data lake

Staff export what they see as a PDF. There is no CSV button in the pages yet. For other
systems, the API returns every page as CSV: add
`format=csv` to the page's address, with the same cohort and filters the page uses.

| Page | CSV address (after your site's address) |
| --- | --- |
| Student paths | `/api/v1/uncf/student-paths?cohort=2023-24&format=csv` |
| DFW courses | `/api/v1/uncf/dfw?cohort=2023-24&format=csv` |
| One DFW course | `/api/v1/uncf/dfw/course?course=ENG%20101&cohort=2023-24&format=csv` |
| Gateway courses | `/api/v1/uncf/gateway?cohort=2023-24&format=csv` |
| Credit momentum | `/api/v1/uncf/credit-momentum?cohort=2023-24&format=csv` |
| One measure by group | `/api/v1/uncf/measures/retention?cohort=2023-24&group_by=pell&format=csv` |

Each row starts with the cohort, filters and retention type it answers. Filters such as `pell=Y` or
`retention_type=federal` work the same as on the pages. The API's own `/docs` page lists every option
(on your server, `http://127.0.0.1:8001/docs`).

- **Power BI:** Get data, Web, and paste the address.
- **A scheduled job:** fetch the addresses on a schedule and drop the files into the data lake.

If sign in sits in front of the app (section 7), give the job its own way through, such as a separate
internal address that only the job's server can reach.

## 10. Before real data goes in

- [ ] **Approval.** Your data governance office approves where the data will live (your server, or
      Vercel for Path A).
- [ ] **Sign in.** Access is limited to the people who should see it (section 7).
- [ ] **Minimum group size.** The pages show every group, including groups of one student. That was a
      stakeholder request on mock data. Decide with your data owner whether small groups must be hidden
      for FERPA before real data goes in; it is a change in `measures/`.
- [ ] **Column names.** The loader maps the mock files' column names (`data/dictionaries/column_lookup.csv`
      and `normalized-data-model/config/*_mapping.yaml`). Check that your files' headers match, or update
      the mapping files, before the first load.
- [ ] **First load report.** Read the rows held back and why, in `normalized-data-model/logs/`.
- [ ] **Data fixes.** Review the mock data fixes (section 5).
- [ ] **Coverage.** Fill in your analytics config (section 5).
- [ ] **Gateway courses.** The Gateway page lists the courses your course file flags as gateway math (M)
      or English (E). If your files don't set that flag, the page has no courses to show and the gateway
      measures say "not reported".
- [ ] **Labels.** `UNCF_DATA_LABEL=institution` and `UNCF_SOURCE` are set (section 4), and the Explorer's
      header badge reads "Institution PDP data", so nobody reads real numbers as a demonstration, or the
      sample as real.
- [ ] **Chat.** Off, or pointed at an approved AI service (section 8).
- [ ] **Clean up.** Working copies from each load are protected and old ones deleted (section 3).
- [ ] **Spot check.** Compare a few numbers with what your office already reports, such as one cohort's
      retention rate.

## 11. Known limits and open items

The full list, including the mock data's bugs, definitions to confirm and what hasn't been tested, is in
[known issues](known-issues.md).

## 12. Notes for developers who extend it

- **Where code goes.** Numbers in `measures/`, chat analyses in `analytics/`, HTTP in `api/`. See
  [AGENTS.md](../AGENTS.md).
- **Extending the chat.** Adding an analysis or a program: [how the chat works](chat.md#extending-it).
- **Checks.** `make check` before every change; `api/tests/test_data_settings.py` covers loading a
  school's files and the settings above.
