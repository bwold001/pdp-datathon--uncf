"use client";

import { Suspense } from "react";

import { cn } from "@/lib/utils";

import { CohortBar, CohortBarFallback } from "./cohort-bar";
import { explorerHeader } from "./explorer-config";
import { ExplorerProvider } from "./explorer-context";
import { explorerFontClass } from "./explorer-fonts";
import { ExplorerHeader } from "./explorer-header";
import { explorerWrap } from "./explorer-styles";
import { ExplorerTabs, ExplorerTabsFallback } from "./explorer-tabs";

import "./explorer-tokens.css";

/**
 * The Explorer's own app shell: the header and horizontal tabs from the design, the cohort bar every tab shares,
 * then the current tab's page. Always light. The tabs and cohort bar read the URL, so they sit in Suspense with a
 * same-size fallback for the first paint.
 */
export function ExplorerShell({ children }: { children: React.ReactNode }) {
  return (
    <ExplorerProvider>
      {/* data-pdf-page: what Share Insight draws. */}
      <div data-pdf-page className={cn(explorerFontClass, "flex min-h-svh flex-col bg-(--uncf-bg) text-[15px] [color-scheme:light] leading-normal text-(--uncf-ink)")}>
        <ExplorerHeader />
        <Suspense fallback={<ExplorerTabsFallback />}>
          <ExplorerTabs />
        </Suspense>
        <Suspense fallback={<CohortBarFallback />}>
          <CohortBar />
        </Suspense>
        <main className={cn(explorerWrap, "flex flex-1 flex-col gap-7 pt-10 pb-14")}>{children}</main>
        <p className={cn(explorerWrap, "pb-6 text-center text-[13px] text-(--uncf-ink-3)")}>{explorerHeader.disclaimer}</p>
      </div>
    </ExplorerProvider>
  );
}
