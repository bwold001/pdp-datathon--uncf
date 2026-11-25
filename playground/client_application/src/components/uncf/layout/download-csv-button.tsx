"use client";

import { Download } from "lucide-react";
import { Suspense } from "react";

import { env } from "@/lib/env";
import { cn } from "@/lib/utils";

import { explorerButton } from "./explorer-styles";
import { useCohortFilters } from "./use-cohort-filters";

/** The address of a page's CSV: its API path with the cohort bar's query (defaults included) and format=csv. */
export function csvHref(path: string, apiQuery: string): string {
  return `${env.apiBaseUrl}${path}?${apiQuery ? `${apiQuery}&` : ""}format=csv`;
}

/**
 * Download CSV, beside Share Insight: the numbers behind the page for the chosen cohort, filters and retention
 * measure, as the API writes them (api/route.py). The columns are the same for every cohort and filter, so a file
 * can be imported into Power BI or a spreadsheet the same way each time.
 */
export function DownloadCsvButton({ path }: { path: string }) {
  // It reads the cohort bar from the URL, which Next.js only allows inside a Suspense boundary on a prerendered
  // page. The boundary lives here so every page can use the button, including in a loading fallback.
  return (
    <Suspense fallback={null}>
      <CsvLink path={path} />
    </Suspense>
  );
}

/** The link itself, with the cohort bar's query. */
function CsvLink({ path }: { path: string }) {
  const { apiQuery } = useCohortFilters();
  return (
    <a href={csvHref(path, apiQuery)} download data-pdf-skip className={cn(explorerButton, "shrink-0 self-start")}>
      <Download className="size-4" aria-hidden />
      Download CSV
    </a>
  );
}
