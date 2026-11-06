"use client";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ContextPanel } from "@/components/workbench/context-panel/context-panel";
import { ContextPanelProvider } from "@/components/workbench/context-panel/context-panel-provider";
import { NavigationPanel, type WorkbenchDestinations } from "@/components/workbench/navigation-panel/navigation-panel";
import { afterUpload, beforeUpload, caveats, fields, terms } from "./context-panel-fixtures";
import { sidebarDestinations } from "./navigation-panel-fixtures";

type WorkbenchStorybookWrapperProps = {
  /** Which navigation link is current. */
  page: Exclude<keyof WorkbenchDestinations, "playground">;
  /** Whether files are saved: sets the database status, the "no data" note and the context panel's copy. */
  hasData: boolean;
  /** The field guide has no context panel; every other page shows it. */
  showContextPanel?: boolean;
  children: React.ReactNode;
};

/** Puts a page story inside DashboardShell with both workbench panels and their synthetic fixtures. */
export function WorkbenchStorybookWrapper({ page, hasData, showContextPanel = true, children }: WorkbenchStorybookWrapperProps) {
  // Profiles are measured from uploaded rows, so a field has none before an upload.
  const contextFields = hasData ? fields : fields.map((field) => ({ ...field, profile: undefined }));
  return (
    <DashboardShell
      leftSidebar={
        <NavigationPanel
          destinations={sidebarDestinations}
          currentPath={sidebarDestinations[page]}
          database={hasData ? { status: "loaded", tables: ["cohort", "course"] } : { status: "empty" }}
        />
      }
      contentProvider={showContextPanel ? ContextPanelProvider : undefined}
      rightSidebar={
        showContextPanel ? (
          <ContextPanel
            fields={contextFields}
            introduction={hasData ? afterUpload : beforeUpload}
            hasData={hasData}
            terms={terms}
            // Caveats describe uploaded rows, so there are none before an upload.
            caveats={hasData ? caveats : []}
          />
        ) : undefined
      }
    >
      {children}
    </DashboardShell>
  );
}
