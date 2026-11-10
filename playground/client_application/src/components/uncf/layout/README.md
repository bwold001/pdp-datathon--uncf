# Explorer shell

The shell every Explorer tab shares, as in the team design
(https://claude.ai/artifact/XeFCVWwP8Ct8CfjXJU9JtC): the header, the horizontal tab row and the grey cohort bar.
It replaces the app's left sidebar on these pages, so the pages live in their own route group,
`src/app/(uncf-explorer)/`, like the workbench's `(dashboard)`.

| Tab | Page | URL | API |
| --- | --- | --- | --- |
| Student paths | `src/app/(uncf-explorer)/uncf/paths/page.tsx` | `/uncf/paths` | `GET /api/v1/uncf/student-paths` |
| DFW | `src/app/(uncf-explorer)/uncf/dfw/page.tsx` | `/uncf/dfw` | |
| Gateway courses | `src/app/(uncf-explorer)/uncf/gateway/page.tsx` | `/uncf/gateway` | |
| Credit momentum | `src/app/(uncf-explorer)/uncf/credit-momentum/page.tsx` | `/uncf/credit-momentum` | |
| Chat | `src/app/(uncf-explorer)/uncf/chat/page.tsx` | `/uncf/chat` | |

The numbers come from the shared API (`api/route.py`), which takes every number from `measures/` and is mounted in
the Playground server under `/api/v1`. The tabs do no counting. The numbers are calculated from the synthetic sample
data, never typed in.

Chat components and stories live in `src/components/uncf/chat/`, alongside the other Explorer features.
The old `/chat` and `/sandbox/data-chat-ui` pages redirect to `/uncf/chat`.

## Building a tab

Copy the Student paths tab (`components/uncf/paths/`): a page with a `ViewIntro`, then a client component in
`<Suspense>` that loads its numbers.

- **Filters.** `useCohortFilters()` gives `filters` (each value, `null` for "All") and `apiQuery`, the same as query
  values for your endpoint. Load with `explorerLoader<YourResponse>("/uncf/your-page", apiQuery)` inside `useMemo`,
  then `useApiResource(load)`. The filters live in the URL (`?cohort=2022-23&pell=Y`), so a view can be shared, Back
  works, and they carry across tabs. A tab's own query values (a sort order) stay on that tab.
- **Student count.** `useShowStudentCount(count)` shows "Showing 1,114 students" in the cohort bar.
- **Parts.** `explorer-parts.tsx` has the design's `Card`, `CardHead`, `KpiGrid` and `Kpi`, `Legend`, `TrackBar`,
  `Counted` ("How it's counted"), `Notice`, `MessageCard` (too few students, or an error) and `LoadingBlock`.
- **Hidden numbers.** The API sends groups under 10 students as `null`. Show them with `formatCount` ("Under 10"),
  never as 0.
- **Colors and type.** Use the design's colors from `explorer-tokens.css` in Tailwind, e.g. `bg-(--uncf-surface)`,
  `text-(--uncf-ink-2)`, `border-(--uncf-line)`. IBM Plex Sans is already on; put `uncf-num` on numbers for IBM Plex
  Mono with aligned digits. The Explorer is always light; avoid the app's `ui/` components, which follow dark mode.
- **Stories.** Save a real answer from your endpoint as a fixture (see `paths/paths-fixtures.ts`) and wrap the story in
  `ExplorerStoryFrame`.

## Changing the shell

- **Add a tab:** a page folder under `src/app/(uncf-explorer)/uncf/`, a route in `src/lib/routes.ts`,
  and a line in `explorerTabs` in `explorer-config.ts`.
- **Add a filter:** an entry in `cohortFilters` in `explorer-config.ts`, with the measures' dimension name and
  values (`STUDENT_DIMENSIONS` in `measures/breakdowns/common.py`, values in `measures/models.py`). Every tab gets it.
