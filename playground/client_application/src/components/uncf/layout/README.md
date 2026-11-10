# Explorer shell

The shell every Explorer tab shares, as in the team design
(https://claude.ai/artifact/XeFCVWwP8Ct8CfjXJU9JtC): the header and the horizontal tab row. It replaces
the app's left sidebar on these pages, so the pages live in their own route group,
`src/app/(uncf-explorer)/`, like the workbench's `(dashboard)`.

| Tab | Page | URL |
| --- | --- | --- |
| Student paths | `src/app/(uncf-explorer)/uncf/paths/page.tsx` | `/uncf/paths` |
| DFW | `src/app/(uncf-explorer)/uncf/dfw/page.tsx` | `/uncf/dfw` |
| Gateway courses | `src/app/(uncf-explorer)/uncf/gateway/page.tsx` | `/uncf/gateway` |
| Credit momentum | `src/app/(uncf-explorer)/uncf/credit-momentum/page.tsx` | `/uncf/credit-momentum` |

## Building a tab

Branch from this shell and fill in your tab's `page.tsx`; each one only has its title for now.

- **Colors and type.** Use the design's colors from `explorer-tokens.css` in Tailwind, e.g.
  `bg-(--uncf-surface)`, `text-(--uncf-ink-2)`, `border-(--uncf-line)`. IBM Plex Sans is already on;
  `font-(family-name:--uncf-mono)` gives IBM Plex Mono.
- **Width.** The shell already centers your content at the design's width. `explorerWrap` in
  `explorer-styles.ts` has the same width and gutters if you need them.

## Changing the shell

- **Add a tab:** a page folder under `src/app/(uncf-explorer)/uncf/`, a route in `src/lib/routes.ts`,
  and a line in `explorerTabs` in `explorer-config.ts`.
- **Export:** the header's Export button is off until it's built.
