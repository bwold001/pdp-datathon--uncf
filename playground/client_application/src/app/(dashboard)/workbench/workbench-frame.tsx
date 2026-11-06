"use client";

import { usePathname } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ContextPanel } from "@/components/workbench/context-panel/context-panel";
import { ContextPanelProvider } from "@/components/workbench/context-panel/context-panel-provider";
import { NavigationPanel } from "@/components/workbench/navigation-panel/navigation-panel";
import { afterUpload, beforeUpload } from "@/content/workbench";
import { routes } from "@/lib/routes";
import { databaseState } from "@/services/workbench-mappers";
import { useWorkbenchData } from "@/app/(dashboard)/workbench/workbench-data";

const destinations = {
  home: routes.workbench,
  upload: routes.workbenchUpload,
  explore: routes.workbenchExplore,
  fields: routes.workbenchFields,
  playground: routes.home,
};

/** Wraps workbench pages in navigation and a data-aware context panel. */
export function WorkbenchFrame({ children }: { children: React.ReactNode }) {
  const currentPath = usePathname();
  const { fields, tables, hasData } = useWorkbenchData();
  const terms = fields.map(({ id, title, description }) => ({ id, label: title, description }));
  const showContextPanel = currentPath !== routes.workbenchFields && !currentPath.startsWith(`${routes.workbenchFields}/`);
  const database = databaseState(tables.status === "success" ? tables.data : tables.status);
  return (
    <DashboardShell
      shellTitle="Workbench"
      leftSidebar={
        <NavigationPanel destinations={destinations} currentPath={currentPath} database={database} />
      }
      contentProvider={showContextPanel ? ContextPanelProvider : undefined}
      rightSidebar={showContextPanel ? (
        <ContextPanel fields={fields} introduction={hasData ? afterUpload : beforeUpload} hasData={hasData} terms={terms} />
      ) : undefined}
    >
      {children}
    </DashboardShell>
  );
}
