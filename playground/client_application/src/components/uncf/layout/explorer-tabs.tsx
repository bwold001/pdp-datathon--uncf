"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

import { cn } from "@/lib/utils";

import { cohortFiltersToUrl, readCohortFilters } from "./cohort-filters";
import { explorerTabs } from "./explorer-config";
import { explorerWrap } from "./explorer-styles";

/** The horizontal tab row. Each link keeps the cohort filters, so switching tabs doesn't reset them. */
export function ExplorerTabs() {
  const searchParams = useSearchParams();
  // Only the cohort filters travel between tabs; a tab's own query values stay on that tab.
  const query = cohortFiltersToUrl(readCohortFilters(searchParams)).toString();
  return <TabLinks query={query} />;
}

/** The tab row before the URL's filters are read, for the first paint. */
export function ExplorerTabsFallback() {
  return <TabLinks query="" />;
}

/** The links themselves, with the current tab marked. */
function TabLinks({ query }: { query: string }) {
  const pathname = usePathname();

  return (
    <nav aria-label="Views" className="border-b border-(--uncf-line) bg-(--uncf-surface)">
      <div className={cn(explorerWrap, "flex gap-1.5 overflow-x-auto")}>
        {explorerTabs.map((tab) => {
          const isCurrent = pathname === tab.href || pathname.startsWith(`${tab.href}/`);
          return (
            <Link
              key={tab.href}
              href={query ? `${tab.href}?${query}` : tab.href}
              aria-current={isCurrent ? "page" : undefined}
              className="border-b-3 border-(--uncf-blue-soft) px-4.5 pt-2 pb-3 font-medium whitespace-nowrap text-(--uncf-ink-2) hover:text-(--uncf-ink) aria-[current=page]:border-(--uncf-blue) aria-[current=page]:text-(--uncf-blue)"
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
