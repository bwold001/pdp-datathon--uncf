"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

import { explorerTabs } from "./explorer-config";
import { explorerWrap } from "./explorer-styles";

/** The horizontal tab row under the header, with the current tab marked. */
export function ExplorerTabs() {
  const pathname = usePathname();

  return (
    <nav aria-label="Views" className="border-b border-(--uncf-line) bg-(--uncf-surface)">
      <div className={cn(explorerWrap, "flex gap-1.5 overflow-x-auto")}>
        {explorerTabs.map((tab) => {
          const isCurrent = pathname === tab.href || pathname.startsWith(`${tab.href}/`);
          return (
            <Link
              key={tab.href}
              href={tab.href}
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
