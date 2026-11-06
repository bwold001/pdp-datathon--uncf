"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useSidebar } from "@/components/ui/sidebar";

type PanelSelection = { view: "about"; fieldId: null } | { view: "field"; fieldId: string };
type ContextPanelState = PanelSelection & { openField: (fieldId: string) => void; showAboutData: () => void };
const ContextPanelContext = createContext<ContextPanelState | null>(null);

/** Pass as DashboardShell.contentProvider so useSidebar targets the right panel. */
export function ContextPanelProvider({ children }: { children: ReactNode }) {
  const [selection, setSelection] = useState<PanelSelection>({ view: "about", fieldId: null });
  const { isMobile, setOpen, setOpenMobile } = useSidebar();
  /** Select a field and open the desktop panel or mobile sheet. */
  function openField(fieldId: string) {
    setSelection({ view: "field", fieldId });
    if (isMobile) setOpenMobile(true);
    else setOpen(true);
  }
  /** Return to the data overview without closing the panel. */
  function showAboutData() {
    setSelection({ view: "about", fieldId: null });
  }
  return <ContextPanelContext.Provider value={{ ...selection, openField, showAboutData }}>{children}</ContextPanelContext.Provider>;
}

/** Read the selected field and context-panel actions from the provider. */
export function useContextPanel() {
  const context = useContext(ContextPanelContext);
  if (!context) throw new Error("useContextPanel must be used within ContextPanelProvider.");
  return context;
}

