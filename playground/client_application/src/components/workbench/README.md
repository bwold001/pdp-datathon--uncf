# Workbench integration

`components/layout/` contains the generic shell: `DashboardShell`, `DashboardHeader`,
`DashboardSidebar` and `SidebarNavMenu`. These building blocks take caller-supplied content
and have no Workbench dependency.

`components/workbench/context-panel/` contains `ContextPanel`, its selection provider and
its About data and field-detail content. `components/workbench/navigation-panel/` contains
`NavigationPanel` and `DatabaseStatus`. Reusable dictionary types and presentation live in
`components/workbench/shared/`: `dictionary-types.ts`, `CodeMeaningList`, `TermList` and
`ValueDistribution`. Each page and its parts live in `home/`, `upload/`, `explore/` or
`field-guide/`. There is no `pages/` folder. `UploadStatusLine` belongs to Home;
`UploadedFileList` belongs to Upload; `FilteredStudentsSummary` belongs to Explore;
`FieldGroupToggle` and `FieldGuideArticle` belong to the Field guide.

Synthetic story data lives in `components/testing/context-panel-fixtures.ts` and
`components/testing/navigation-panel-fixtures.ts`. The panel stories are
**Workbench/Context (right) panel** and **Workbench/Navigation (left) panel**.

Pass `ContextPanelProvider` as `DashboardShell.contentProvider` so it wraps the page and
right panel inside the right `SidebarProvider`. This makes `useContextPanel().openField()`
open the correct desktop panel or mobile sheet. Place `ContextPanel` in `rightSidebar` and
`NavigationPanel` in `leftSidebar`.

Keep `DashboardShell` mounted in a shared route layout to preserve the selected field across
navigation.

For example, mount a client layout at `app/workbench/layout.tsx`. The application supplies the
live dictionary and database state; the imports below use synthetic fixtures only to make the
composition copyable.

```tsx
"use client";

import { usePathname } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ContextPanel } from "@/components/workbench/context-panel/context-panel";
import { ContextPanelProvider } from "@/components/workbench/context-panel/context-panel-provider";
import { NavigationPanel } from "@/components/workbench/navigation-panel/navigation-panel";
import { beforeUpload, fields, terms } from "@/components/testing/context-panel-fixtures";

const destinations = {
  home: "/workbench", upload: "/workbench/upload",
  explore: "/workbench/explore", fields: "/workbench/fields",
};

/** Keep the selected field mounted while child pages change. */
export default function WorkbenchLayout({ children }: { children: React.ReactNode }) {
  const currentPath = usePathname();
  return (
    <DashboardShell
      leftSidebar={<NavigationPanel destinations={destinations} currentPath={currentPath} database={{ status: "empty" }} />}
      contentProvider={ContextPanelProvider}
      rightSidebar={<ContextPanel fields={fields} terms={terms} introduction={beforeUpload} hasData={false} />}
    >
      {children}
    </DashboardShell>
  );
}
```

Child pages in this layout provide their own `h1`. For shell props and sidebar-control hooks,
see [DashboardShell](../layout/dashboard-shell.tsx) and its Storybook docs under
**Components → Layout → Dashboard shell**.

Storybook fixtures in `components/testing` are synthetic examples, not measured PDP results
or evidence of a completed upload flow. Routes and database connections must be supplied by
the application.

## Controlled pages

The caller owns data, URL state and navigation. Page components take one prop object per
child, type it with `ComponentProps<typeof Child>`, and spread it into that child. A page
declares only what it owns, such as Upload's stage and error. For example, `FieldGuidePage`
takes `search`, `groups`, `index` and `detail` objects:

```tsx
type FieldGuidePageProps = {
  search: ComponentProps<typeof FieldSearch>;
  groups: ComponentProps<typeof FieldGroupToggle>;
  index: ComponentProps<typeof FieldIndex>;
  detail: ComponentProps<typeof FieldGuideArticle>;
};

// Inside the page composition:
<FieldSearch {...search} />
<FieldGroupToggle {...groups} />
<FieldIndex {...index} />
<FieldGuideArticle {...detail} />
```

Import `ComponentProps` from React and the children from their feature folder. Home uses a
discriminated union so callers pass only the active view's props:

```tsx
type HomePageProps = {
  tools: ComponentProps<typeof TeamToolsSection>;
} & (
  | { hasData: false; firstRun: ComponentProps<typeof HomeFirstRun>; dataLoaded?: never }
  | { hasData: true; dataLoaded: ComponentProps<typeof HomeDataLoaded>; firstRun?: never }
);
```

Home spreads `firstRun` or `dataLoaded` into the selected child. Team tools appear when
`tools.tools.length > 0`. Explore derives whether filters are active from their selected
values; each filter menu keeps its own open state and search text unless its open state is
explicitly controlled. The plain-language/Analyst toggle remains controlled by the caller.

Preview a page inside `WorkbenchStorybookWrapper` from
`components/testing/workbench-storybook-wrapper.tsx`. Set `page` to `home`, `upload`,
`explore` or `fields`, and use `showContextPanel={false}` for the Field guide. Fixtures in
`home-fixtures.ts`, `upload-fixtures.ts`, `explore-fixtures.ts` and `field-guide-fixtures.ts`
show synthetic examples. The wrapper and fixture controllers stay out of production routes.

Home, Upload, Explore and the Field guide have route controllers under
`app/(dashboard)/workbench/`. Explore pages through the loaded `student` table; its filters and
comparisons wait for API endpoints, so for now they appear only in Storybook.

## Test Upload by hand

Upload's failure states need the real loader, so stories can't show them. To try them in the
running app, make the test files from the repo root:

```bash
python playground/scripts/make_upload_test_files.py
```

They go to `normalized-data-model/output/playground/upload_test_files/`, which git ignores, so
run the script yourself rather than looking for them in the repo. It rebuilds the folder each
time. The files come from the data model's 10-student sample, so they're synthetic. Each case's
`EXPECTED.md` has the steps and what each page should show.

| Case | What it checks |
| --- | --- |
| `1_every_row_fails` | Valid headers, but every cohort row fails: Upload shows an error and the last load is kept |
| `2_clean_files` | Clean cohort and course files: Home shows no warnings |
| `3_one_row_fails` | One bad cohort row: the load saves 9 students and Home counts its warnings |
| `4_leave_during_load` | No files: leave Upload during a load, and Home shows the data without a reload |

## Copy the workbench

Copy these paths under `src/` together:

- `components/workbench/` for feature components, panels and shared dictionary presentation.
- The Workbench fixtures and `workbench-storybook-wrapper.tsx` in `components/testing/` for previews.
- `app/(dashboard)/workbench/` for the layout, shared data provider and route controllers.
- `services/workbench.ts` and `services/workbench-mappers.ts` for API contracts and mapping.
- `hooks/use-pipeline-run.ts` for polling and `content/workbench.ts` for shared copy.

Also supply their shared dependencies: `components/layout/`, the imported `components/ui/*`
primitives, shared components such as `PageIntro`, `SearchInput` and `EmptyState`,
`lib/api-client.ts`, `lib/routes.ts`, and the project's styling and Bun dependencies. The
Workbench does not own those shared pieces. Configure the API base URL for your application.

Page compositions work in any shell. `NavigationPanel` and `ContextPanel` need
`DashboardShell` and its providers as shown above. Workbench components do not import
`sandbox` or `app-shell` code; the playground's sidebar links into the Workbench from outside.
