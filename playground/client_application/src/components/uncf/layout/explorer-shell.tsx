"use client";

import { Suspense } from "react";

import { cn } from "@/lib/utils";

import { CohortBar, CohortBarFallback } from "./cohort-bar";
import type { DataLabel } from "./explorer-api";
import { dataWords } from "./explorer-config";
import { ExplorerProvider, useDataLabel } from "./explorer-context";
import { explorerFontClass } from "./explorer-fonts";
import { ExplorerHeader } from "./explorer-header";
import { explorerWrap } from "./explorer-styles";
import { ExplorerTabs, ExplorerTabsFallback } from "./explorer-tabs";

import "./explorer-tokens.css";

/**
 * The Explorer's own app shell: the header and horizontal tabs from the design, the cohort bar every tab shares,
 * then the current tab's page. Always light. dataLabel fixes what the badge and bottom line say (stories); left out,
 * the API's /uncf/health says. The tabs and cohort bar read the URL, so they sit in Suspense with a
 * same-size fallback for the first paint.
 */
export function ExplorerShell({ children, dataLabel }: { children: React.ReactNode; dataLabel?: DataLabel }) {
  return (
    <ExplorerProvider dataLabel={dataLabel}>
      <div className={cn(explorerFontClass, "flex min-h-svh flex-col bg-(--uncf-bg) text-[15px] [color-scheme:light] leading-normal text-(--uncf-ink)")}>
        <ExplorerHeader />
        <Suspense fallback={<ExplorerTabsFallback />}>
          <ExplorerTabs />
        </Suspense>
        <Suspense fallback={<CohortBarFallback />}>
          <CohortBar />
        </Suspense>
        <main className={cn(explorerWrap, "flex flex-1 flex-col gap-7 pt-10 pb-14")}>{children}</main>
        <DataDisclaimer />
      </div>
    </ExplorerProvider>
  );
}

/** The line at the bottom of every page about what the data is; nothing until the API says. */
function DataDisclaimer() {
  const label = useDataLabel();
  if (!label) return null;
  return <p className={cn(explorerWrap, "pb-6 text-center text-[13px] text-(--uncf-ink-3)")}>{dataWords[label].disclaimer}</p>;
}
