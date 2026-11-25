# Client Application

The Next.js front end for the Student Persistence and Pathway Explorer. It gets all of its data from the
[Server Application](../server_application/README.md). The data is synthetic.

## Layout

```
src/
├── app/
│   ├── layout.tsx, error.tsx, not-found.tsx, globals.css
│   ├── page.tsx                 # / redirects to /uncf/paths
│   └── (uncf-explorer)/uncf/    # One folder per tab: paths, dfw, gateway, credit-momentum, chat
├── components/
│   ├── uncf/                    # The Explorer: one folder per tab, plus layout/ (shell, cohort bar, tabs)
│   ├── chat/panel-chat.tsx      # The chat panel the chat tab uses
│   ├── ui/                      # shadcn/ui pieces still in use
│   └── site-header.tsx, page-shell.tsx, status-page.tsx, ...   # Error and 404 pages
├── content/                     # Words shown on pages: brand.ts, chat-ui.ts
├── hooks/                       # Data loading and chat state
├── lib/                         # Logic with no markup: env.ts, api-client.ts, routes.ts, ...
└── services/                    # One file per API resource
```

How to build an Explorer tab: [`src/components/uncf/layout/README.md`](src/components/uncf/layout/README.md).

**Rule of thumb:** `.tsx` files render. Calling the API, reading the environment, formatting and
mapping data live in `.ts` files in `lib/`, `services/`, `hooks/` and `content/`.

## Run it

Start the Server Application first ([quick start](../../README.md#quick-start-on-the-mock-data)), then:

```bash
mise run web:install && mise run web:dev     # http://localhost:3000
```

Settings are in [`src/lib/env.ts`](src/lib/env.ts). Override them in `.env.local` (git-ignored); the
variables are listed in [`.env.example`](.env.example).

## Storybook

Each Explorer tab has a story with mock data, so a tab can be built and checked without the API:

```bash
mise run web:storybook          # http://localhost:6006
mise run web:test-storybook     # runs every story's play function in Chromium
```
