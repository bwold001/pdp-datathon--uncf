"use client";

import { Check, Download } from "lucide-react";
import { useState } from "react";

import { measures, type Cohort, type Dimension, type PathsQuery, type PathsResponse, type ResultsQuery, type ResultsResponse } from "@/app/(app)/uncf/data";
import { describeError } from "@/lib/errors";

import { buildCsvRows, csvFileName, downloadText, toCsvText } from "./csv";

type CsvDownloadButtonProps = {
  cohort: Cohort;
  groupBy: Dimension[];
  load: (query: ResultsQuery) => Promise<ResultsResponse>;
  loadYearTwo: (query: PathsQuery) => Promise<PathsResponse>;
};

type DownloadState = { status: "idle" } | { status: "working" } | { status: "done"; fileName: string; rows: number } | { status: "error"; message: string };

/** Downloads every outcome and the year-2 paths for this view as one CSV for Excel or Power BI. */
export function CsvDownloadButton({ cohort, groupBy, load, loadYearTwo }: CsvDownloadButtonProps) {
  const [state, setState] = useState<DownloadState>({ status: "idle" });

  /** Load the view's rows, build the file and save it. */
  async function download() {
    setState({ status: "working" });
    try {
      // An outcome that isn't saved for this view is left out rather than failing the whole file.
      const loaded = await Promise.all(measures.map((measure) => load({ measure, cohort, groupBy }).catch(() => null)));
      const outcomes = loaded.filter((response): response is ResultsResponse => response !== null);
      if (outcomes.length === 0) throw new Error("None of the outcomes are saved for this view.");
      const paths = await loadYearTwo({ cohort, groupBy }).catch(() => null);
      const rows = buildCsvRows(outcomes, paths);
      const fileName = csvFileName(cohort, groupBy);
      downloadText(fileName, toCsvText(rows));
      setState({ status: "done", fileName, rows: rows.length });
    } catch (error) {
      setState({ status: "error", message: describeError(error) });
    }
  }

  return (
    <span className="inline-flex flex-wrap items-center gap-2">
      <span role="status" aria-live="polite" className="text-xs text-muted-foreground">
        {state.status === "done" && `${state.rows} rows saved to ${state.fileName}. Hidden numbers are blank with a status, never 0.`}
        {state.status === "error" && `The CSV couldn't be made: ${state.message}`}
      </span>
      <button
        type="button"
        onClick={download}
        disabled={state.status === "working"}
        className="inline-flex h-10 items-center gap-2 rounded-lg border border-foreground/30 bg-background px-4 text-sm font-medium hover:bg-muted focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-60"
      >
        {state.status === "done" ? <Check className="size-4" aria-hidden /> : <Download className="size-4" aria-hidden />}
        {state.status === "working" ? "Preparing…" : state.status === "done" ? "Downloaded" : "Download CSV"}
      </button>
    </span>
  );
}
