# Explorer shell

The shell every Explorer tab shares, as in the team design
(https://claude.ai/artifact/XeFCVWwP8Ct8CfjXJU9JtC): the header, the horizontal tab row and the grey cohort bar.
It replaces the app's left sidebar on these pages, so the pages live in their own route group,
`src/app/(uncf-explorer)/`, like the workbench's `(dashboard)`.

| Tab | Page | URL | API |
| --- | --- | --- | --- |
| Student paths | `src/app/(uncf-explorer)/uncf/paths/page.tsx` | `/uncf/paths` | `GET /api/v1/uncf/student-paths` |
| DFW | `src/app/(uncf-explorer)/uncf/dfw/page.tsx` | `/uncf/dfw` | `GET /api/v1/uncf/dfw`, `/dfw/course` |
| Gateway courses | `src/app/(uncf-explorer)/uncf/gateway/page.tsx` | `/uncf/gateway` | `GET /api/v1/uncf/gateway` |
| Credit momentum | `src/app/(uncf-explorer)/uncf/credit-momentum/page.tsx` | `/uncf/credit-momentum` | `GET /api/v1/uncf/credit-momentum` |
| Chat | `src/app/(uncf-explorer)/uncf/chat/page.tsx` | `/uncf/chat` | |

**Share Insight** (`share-insight-button.tsx`) sits beside each tab's title: `ViewIntro` draws it, and Credit
momentum, which draws its own heading, adds it there. It downloads the tab as one long PDF page with no page breaks.
The PDF is a report, not a screenshot (`share-insight-report.tsx`): the Explorer's name and source, who's counted in
words ("Cohort 2023-24 · 594 students · Pell (year 1): Pell recipient") instead of the tabs and cohort bar, then a copy
of the tab. Mark a control `data-pdf-skip` to leave it out (sort menus, "Show 10 more", "Try again"). It's drawn in
the browser (`html-to-image`, then `jspdf`), off screen, so the page doesn't change; the PDF's text is part of the
picture, not selectable. It doesn't print: print lays the page out again for the paper and splits it.

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
  works, and the ones someone set carry across tabs. A tab's own query values (a sort order) stay on that tab.
- **Retention.** Gateway and Credit momentum show a Retention filter: `school` (the PDP flag, "Returned here", the
  API's default) or `federal` ("Back next fall"). Name the measure from the answer's `meta.retention_type` with
  `retentionWords()` in `explorer-parts.tsx`, never a fixed "next fall".
- **No math in the tab.** Shares, gaps, totals and hiding come from the API (`measures/`); a tab only formats and
  draws them.
- **Student count.** `useShowStudentCount(count)` shows "Showing 1,114 students" in the cohort bar.
- **Parts.** `explorer-parts.tsx` has the design's `Card`, `CardHead`, `KpiGrid` and `Kpi`, `Legend`, `TrackBar`,
  `Counted` ("How it's counted"), `Notice`, `MessageCard` (too few students, or an error) and `LoadingBlock`.
- **Hidden numbers.** The API sends groups under `meta.min_students` as `null` (the server's `UNCF_MIN_STUDENTS`,
  1 by default). Show them with `formatCount(count, meta.min_students)` ("Under 10", or "None" at 1), never as 0.
  Word notes about hidden groups with `small-groups.ts`, which says nothing is hidden when the minimum is 1.
- **Colors and type.** Use the design's colors from `explorer-tokens.css` in Tailwind, e.g. `bg-(--uncf-surface)`,
  `text-(--uncf-ink-2)`, `border-(--uncf-line)`. IBM Plex Sans is already on; put `uncf-num` on numbers for IBM Plex
  Mono with aligned digits. The Explorer is always light; avoid the app's `ui/` components, which follow dark mode.
- **Stories.** Save a real answer from your endpoint as a fixture (see `paths/paths-fixtures.ts`) and wrap the story in
  `ExplorerStoryFrame`. To test a whole tab with its loading, answer `fetch` from the fixtures (see
  `dfw/dfw-page.stories.tsx`).

## Changing the shell

- **Add a tab:** a page folder under `src/app/(uncf-explorer)/uncf/`, a route in `src/lib/routes.ts`,
  and a line in `explorerTabs` in `explorer-config.ts`.
- **Add a filter:** an entry in `cohortFilters` in `explorer-config.ts`, with the measures' dimension name and
  values (`STUDENT_DIMENSIONS` in `measures/breakdowns/common.py`, values in `measures/models.py`). Every tab gets it,
  unless you list the tabs that show it in `tabs`.
- **Start a filter somewhere else on one tab:** a line in `tabFilterDefaults` (Student paths starts Enrollment type at
  First-time, as in the design). "All" is then `all` in the URL.
