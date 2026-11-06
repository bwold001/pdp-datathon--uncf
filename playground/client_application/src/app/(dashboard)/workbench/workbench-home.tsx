"use client";

import { useCallback } from "react";
import { CircleX } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { HomePage, type HomePageProps } from "@/components/workbench/home/home-page";
import type { HomeStat } from "@/components/workbench/home/home-data-loaded";
import type { StarterQuestion } from "@/components/workbench/home/starter-question-list";
import { useApiResource } from "@/hooks/use-api-resource";
import { routes } from "@/lib/routes";
import { warningCount } from "@/services/workbench-mappers";
import { getRun, getTableRows, type TableSummary } from "@/services/workbench";
import { useWorkbenchData } from "@/app/(dashboard)/workbench/workbench-data";

const statTables = [
  { table: "student", label: "students" },
  { table: "cohort_membership", label: "cohort memberships" },
  { table: "course_enrollment", label: "course records" },
];
// Explore doesn't read these filters yet; the query strings keep each link distinct until it does.
const starterQuestions: StarterQuestion[] = [
  { question: "How many students receive Pell grants?", filterHint: "Pell = Yes", href: `${routes.workbenchExplore}?pell=yes` },
  { question: "Who has completed gateway math?", filterHint: "Gateway math = Complete", href: `${routes.workbenchExplore}?gateway_math=complete` },
];
const dateFormat =new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" });

/** Formats the database's row counts for Home's stat tiles. */
function homeStats(tables: TableSummary[]): HomeStat[] {
  return statTables.map(({ table, label }) => ({
    id: table,
    value: (tables.find((summary) => summary.name === table)?.row_count ?? 0).toLocaleString("en-US"),
    label,
  }));
}

/** Reads the single load_run row describing the current database replacement. */
async function loadLastRun() {
  const { rows } = await getTableRows("load_run", 1);
  const { run_id: runId, finished_at: finishedAt } = rows[0] ?? {};
  // SQLite timestamps may omit the UTC offset; interpret them the same way as the API's dates.
  const timestamp = typeof finishedAt === "string"
    ? new Date(/(Z|[+-]\d\d:\d\d)$/i.test(finishedAt) ? finishedAt : `${finishedAt}Z`)
    : null;
  const lastUpload = timestamp && !Number.isNaN(timestamp.getTime()) ? dateFormat.format(timestamp) : "at an unknown time";
  const run = typeof runId === "string" ? await getRun(runId) : null;
  return { lastUpload, warningCount: run?.summary ? warningCount(run.summary) : null };
}

/** Owns Home's API state and loads synthetic mock files when requested. */
export function WorkbenchHome() {
  const { tables, hasData, refreshTables, run } = useWorkbenchData();
  const loadLastRunForTables = useCallback(
    () => tables.status === "success" && hasData ? loadLastRun() : Promise.resolve(null),
    [tables, hasData],
  );
  const { resource: lastRun } = useApiResource(loadLastRunForTables);

  /** Load the mock files; the data provider refreshes the counts when the load succeeds. */
  function handleUseMockData() {
    void run.start();
  }

  if (tables.status === "loading") {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
        <Spinner aria-hidden />
        Checking the database…
      </p>
    );
  }
  if (tables.status === "error") {
    return (
      <Alert variant="destructive">
        <CircleX aria-hidden />
        <AlertTitle>The database can&apos;t be reached</AlertTitle>
        <AlertDescription>
          <p>{tables.message}</p>
          <Button variant="outline" onClick={() => void refreshTables()}>Try again</Button>
        </AlertDescription>
      </Alert>
    );
  }
  const props: HomePageProps = hasData ? {
    hasData: true,
    tools: { tools: [] },
    dataLoaded: {
      stats: homeStats(tables.data),
      lastUpload: lastRun.status === "success" && lastRun.data
        ? lastRun.data
        : { lastUpload: lastRun.status === "loading" ? "…" : "at an unknown time", warningCount: null },
      questions: { questions: starterQuestions },
    },
  } : {
    hasData: false,
    tools: { tools: [] },
    firstRun: {
      uploadHref: routes.workbenchUpload,
      fieldGuideHref: routes.workbenchFields,
      onUseMockData: handleUseMockData,
      loadingMockData: run.state.status === "running",
    },
  };
  return (
    <>
      {run.state.status === "failed" && (
        <Alert variant="destructive">
          <CircleX aria-hidden />
          <AlertTitle>The last load didn&apos;t finish</AlertTitle>
          <AlertDescription>
            <p>{run.state.message}</p>
          </AlertDescription>
        </Alert>
      )}
      <HomePage {...props} />
      <p className="text-xs text-muted-foreground">
        The mock data is synthetic: nothing built on it is a finding about real students or institutions.
      </p>
    </>
  );
}
