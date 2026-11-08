"use client";

import { useMemo, useState } from "react";

import {
  loadResults,
  measures,
  type Cohort,
  type Dimension,
  type Measure,
  type ResultsQuery,
  type ResultsResponse,
} from "@/app/(app)/uncf/data";
import { LoadError } from "@/components/load-error";
import { Skeleton } from "@/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useApiResource } from "@/hooks/use-api-resource";

import { buildBars, chartTitle, comparisonSentence } from "./bars";
import { DefinitionPanel } from "./definition-panel";
import { type DetailMode, ExplorerControls, selectedToggle } from "./explorer-controls";
import { cohortLabel, measureNames } from "./labels";
import { ResultsChart } from "./results-chart";

type ExplorerProps = {
  /** Where results come from. Stories pass their own; the page uses the fixture until the #5 API lands. */
  load?: (query: ResultsQuery) => Promise<ResultsResponse>;
  initialCohort?: Cohort;
  initialFirst?: Dimension;
  initialSecond?: Dimension | null;
  initialMeasure?: Measure;
};

/** The Student Success Explorer: pick a class and up to two groupings, see each outcome by group with its definition beside it. */
export function Explorer({
  load = loadResults,
  initialCohort = "2022-23",
  initialFirst = "pell",
  initialSecond = null,
  initialMeasure = "retention",
}: ExplorerProps) {
  const [cohort, setCohort] = useState<Cohort>(initialCohort);
  const [first, setFirst] = useState<Dimension>(initialFirst);
  const [second, setSecond] = useState<Dimension | null>(initialSecond);
  const [measure, setMeasure] = useState<Measure>(initialMeasure);
  const [mode, setMode] = useState<DetailMode>("plain");

  const loader = useMemo(
    () => () => load({ measure, cohort, groupBy: second ? [first, second] : [first] }),
    [load, measure, cohort, first, second],
  );
  const { resource, retry } = useApiResource(loader);

  return (
    <div className="flex flex-col gap-6">
      <ExplorerControls
        cohort={cohort}
        first={first}
        second={second}
        mode={mode}
        onCohortChange={setCohort}
        onFirstChange={setFirst}
        onSecondChange={setSecond}
        onModeChange={setMode}
      />

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <section aria-labelledby="results-heading" className="flex min-w-0 flex-col gap-5 rounded-2xl border bg-card p-5 sm:p-6">
          <div className="flex flex-col gap-3">
            <ToggleGroup
              aria-label="Outcome"
              multiple={false}
              value={[measure]}
              onValueChange={(values) => {
                const next = values[0];
                if (isMeasure(next)) setMeasure(next);
              }}
              variant="outline"
              className="max-w-full flex-wrap"
            >
              {measures.map((value) => (
                <ToggleGroupItem key={value} value={value} className={selectedToggle}>
                  {measureNames[value]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          {resource.status === "loading" && <ResultsSkeleton />}
          {resource.status === "error" && (
            <LoadError title="These results couldn't load." message={resource.message} onRetry={retry} className="min-h-56" />
          )}
          {resource.status === "success" && <Results response={resource.data} mode={mode} />}
        </section>

        {resource.status === "success" && <ResultsDefinition response={resource.data} mode={mode} />}
      </div>

      <p role="status" aria-live="polite" className="sr-only">
        {resource.status === "success"
          ? `Showing ${chartTitle(resource.data)}, students who entered in ${cohortLabel(resource.data.meta.cohort)}.`
          : ""}
      </p>
    </div>
  );
}

/** The chart, its title and the comparison sentence for one loaded response. */
function Results({ response, mode }: { response: ResultsResponse; mode: DetailMode }) {
  const { everyone, sections } = buildBars(response);
  const isGateway = response.meta.measure !== "retention";
  const leftOut = everyone?.state === "ok" ? leftOutOf(response) : null;
  return (
    <>
      <div className="flex flex-col gap-2">
        <h2 id="results-heading" className="text-lg font-semibold tracking-tight">
          {chartTitle(response)} · entered {cohortLabel(response.meta.cohort)}
        </h2>
        <p className="text-sm text-muted-foreground">{response.meta.definition.what}</p>
        <p className="text-[15px] leading-relaxed">
          {comparisonSentence(response, everyone, sections)}{" "}
          <span className="text-muted-foreground">A gap shows a difference between groups, not its cause.</span>
        </p>
      </div>
      <ResultsChart measure={response.meta.measure} everyone={everyone} sections={sections} mode={mode} />
      {isGateway && (
        <p role="note" className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100">
          <strong className="font-semibold">Read gateway rates with care.</strong> A required student with no recorded attempt counts
          as not passing, which lowers the rate.
          {leftOut !== null && leftOut > 0 && ` ${leftOut.toLocaleString("en-US")} more students are left out because their requirement or result is unknown.`}
        </p>
      )}
    </>
  );
}

/** The definition panel for one loaded response. */
function ResultsDefinition({ response, mode }: { response: ResultsResponse; mode: DetailMode }) {
  const { everyone, sections } = buildBars(response);
  return <DefinitionPanel meta={response.meta} everyone={everyone} sections={sections} leftOut={leftOutOf(response)} mode={mode} />;
}

/** True when a toggle value is one of the outcomes. */
function isMeasure(value: unknown): value is Measure {
  return measures.some((measure) => measure === value);
}

/** Students left out of the all-students rate, from its row. */
function leftOutOf(response: ResultsResponse): number | null {
  const everyoneRow = response.rows.find((row) => Object.keys(row.group).length === 0);
  return everyoneRow?.n_excluded ?? null;
}

/** Placeholder bars while results load. */
function ResultsSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading results">
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="h-4 w-1/2" />
      {[0, 1, 2, 3].map((index) => (
        <Skeleton key={index} className="h-8 rounded-lg" />
      ))}
    </div>
  );
}
