"use client";

import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { AboutDataContent, type AboutDataContentProps } from "./about-data-content";
import { FieldDetailsContent } from "./field-details-content";
import type { FieldDefinition } from "@/components/workbench/shared/dictionary-types";
import { useContextPanel } from "./context-panel-provider";

export type ContextPanelProps = AboutDataContentProps & { fields: FieldDefinition[] };

/** Adapts shared selection to presentation; terms and caveats are read-only. */
export function ContextPanel({ fields, ...about }: ContextPanelProps) {
  const { view, fieldId, showAboutData } = useContextPanel();
  return (
    <DashboardSidebar>
      {view === "field"
        ? <FieldDetailsContent field={fields.find((field) => field.id === fieldId)} onBack={showAboutData} />
        : <AboutDataContent {...about} />}
    </DashboardSidebar>
  );
}
