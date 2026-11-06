"use client";

import { ArrowLeftIcon, BookOpenIcon, HouseIcon, TableIcon, UploadIcon } from "lucide-react";
import Link from "next/link";
import { DatabaseStatus, type DatabaseState } from "@/components/workbench/navigation-panel/database-status";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { SidebarNavMenu, type SidebarNavMenuItem } from "@/components/layout/sidebar-nav-menu";
import { useSidebar } from "@/components/ui/sidebar";

export type WorkbenchDestinations = { home: string; upload: string; explore: string; fields: string; playground?: string };
export type NavigationPanelProps = { destinations: WorkbenchDestinations; currentPath: string; database: DatabaseState };

/** Place in DashboardShell.leftSidebar: the left provider owns mobile sheet closing. */
export function NavigationPanel({ destinations, currentPath, database }: NavigationPanelProps) {
  const { isMobile, setOpenMobile } = useSidebar();
  const items: SidebarNavMenuItem[] = [
    { label: "Home", href: destinations.home, icon: HouseIcon },
    { label: "Upload files", href: destinations.upload, icon: UploadIcon },
    { label: "Explore data", href: destinations.explore, icon: TableIcon, note: database.status === "empty" ? "no data" : undefined },
    { label: "Field guide", href: destinations.fields, icon: BookOpenIcon },
  ];
  // Prefer exact matches, then the longest child-route match; Home cannot match every route.
  const activeHref = items.find((item) => item.href === currentPath)?.href
    ?? items.filter((item) => item.href !== destinations.home && currentPath.startsWith(`${item.href}/`))
      .sort((a, b) => b.href.length - a.href.length)[0]?.href;
  return (
    <DashboardSidebar
      title="AR Workbench"
      shortTitle="AR"
      footer={<>
        {destinations.playground && (
          <Link href={destinations.playground} aria-label="Back to playground" className="flex items-center gap-2 rounded-md px-2 py-2 text-sm hover:bg-muted" onClick={() => { if (isMobile) setOpenMobile(false); }}>
            <ArrowLeftIcon aria-hidden className="size-4 shrink-0" />
            <span className="group-data-[collapsible=icon]:hidden">Back to playground</span>
          </Link>
        )}
        <div className="group-data-[collapsible=icon]:hidden"><DatabaseStatus state={database} /></div>
        <div className="hidden group-data-[collapsible=icon]:block"><DatabaseStatus state={database} compact /></div>
      </>}
    >
      <SidebarNavMenu items={items} activeHref={activeHref} label="Workbench" onNavigate={() => { if (isMobile) setOpenMobile(false); }} />
    </DashboardSidebar>
  );
}
