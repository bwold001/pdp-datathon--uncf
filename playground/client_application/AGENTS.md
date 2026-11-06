<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Storybook MCP

Storybook serves an MCP server, `playground-storybook` in the repo's `.mcp.json`, while it runs
(`mise run web:storybook`, http://localhost:6006). Use it when working on components:

- If the component has a story, use `docs-show` for its props and examples; use `docs-list` to find
  available component documentation. For components without stories, read the component source.
- Before writing or changing a story, follow `get-storybook-story-instructions`.
- After changing a component or story, check your work with `test-run` (requires
  `@storybook/addon-vitest`).
- Don't set `parameters.docs.story.inline: false` or `iframeHeight` for stories with sidebars or
  `DashboardShell`. `.storybook/preview.tsx` keeps fixed sidebars inside their docs example. Each
  iframe runs its story's play function on the docs page, which can make the page jump, and each one
  slows the page down.

If the tools aren't available, start Storybook or read the `*.stories.tsx` file next to the component.
If there is no story, read the component source.
