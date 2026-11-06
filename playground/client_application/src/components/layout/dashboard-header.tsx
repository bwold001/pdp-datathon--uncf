"use client";

import { PanelLeftIcon, PanelRightIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useSidebar } from "@/components/ui/sidebar";

type SidebarState = ReturnType<typeof useSidebar>;

/** On phones a sidebar is a sheet with its own open state. */
function isOpen(sidebar: SidebarState) {
  return sidebar.isMobile ? sidebar.openMobile : sidebar.open;
}

/**
 * Top bar of `DashboardShell`: left toggle, shell label, right toggle. It renders inside the right sidebar's
 * provider, so `useSidebar()` here is the right sidebar and the left one comes in as `left`.
 */
export function DashboardHeader({ shellTitle, left, showLeftSidebar = true, showRightSidebar = true }: { shellTitle?: string; left: SidebarState; showLeftSidebar?: boolean; showRightSidebar?: boolean }) {
  const right = useSidebar();

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
      {showLeftSidebar && <>
        <Button variant="ghost" size="icon-sm" aria-label="Toggle navigation" aria-expanded={isOpen(left)} onClick={left.toggleSidebar}>
          <PanelLeftIcon />
        </Button>
        <Separator orientation="vertical" className="my-4" />
      </>}
      {shellTitle && <span className="truncate text-sm font-medium">{shellTitle}</span>}
      {showRightSidebar && <Button
        variant="ghost"
        size="icon-sm"
        aria-label="Toggle context panel"
        aria-expanded={isOpen(right)}
        onClick={right.toggleSidebar}
        className="ml-auto"
      >
        <PanelRightIcon />
      </Button>}
    </header>
  );
}
