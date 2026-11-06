"use client";

import { createContext, Fragment, useContext } from "react";

import { DashboardHeader } from "@/components/layout/dashboard-header";
import { Sidebar, SidebarInset, SidebarProvider, SidebarRail, useSidebar } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

type SidebarState = ReturnType<typeof useSidebar>;
const LeftSidebarContext = createContext<SidebarState | null>(null);
const RightSidebarContext = createContext<SidebarState | null>(null);

/** Read navigation state explicitly; bare useSidebar() in page content returns the right panel. */
export function useLeftSidebar() {
  const sidebar = useContext(LeftSidebarContext);
  if (!sidebar) throw new Error("useLeftSidebar must be used within DashboardShell.");
  return sidebar;
}

/** Read details-panel state explicitly; bare useSidebar() in page content also returns this panel. */
export function useRightSidebar() {
  const sidebar = useContext(RightSidebarContext);
  if (!sidebar) throw new Error("useRightSidebar must be used within DashboardShell's content area.");
  return sidebar;
}

/** Capture navigation state before the details provider shadows it. */
function LeftSidebarProvider({ children }: { children: React.ReactNode }) {
  const sidebar = useSidebar();
  return <LeftSidebarContext.Provider value={sidebar}>{children}</LeftSidebarContext.Provider>;
}

/** Expose details state to the content provider, page, and right panel. */
function RightSidebarProvider({ children }: { children: React.ReactNode }) {
  const sidebar = useSidebar();
  return <RightSidebarContext.Provider value={sidebar}>{children}</RightSidebarContext.Provider>;
}

type DashboardShellProps = {
  /** Optional plain-text label in the top bar. */
  shellTitle?: string;
  /** Navigation. Compose with `DashboardSidebar`; collapses to icons. Omit for no navigation or left toggle. */
  leftSidebar?: React.ReactNode;
  /** Context panel, such as filters or details. Compose with `DashboardSidebar`; collapses off the screen. */
  rightSidebar?: React.ReactNode;
  /** Wraps the page and right panel inside the right SidebarProvider; bare useSidebar() reads that panel. */
  contentProvider?: React.ComponentType<{ children: React.ReactNode }>;
  children: React.ReactNode;
};

/**
 * Full-page dashboard layout: navigation on the left, a context panel on the right, the page in between.
 * Each sidebar is optional and opens and closes on its own; ctrl/cmd+B toggles the left one. Below 768px both
 * open as sheets.
 * It fills the viewport, so use it in place of `PageShell`, not inside it.
 * Use `useLeftSidebar()` or `useRightSidebar()` for page controls: bare `useSidebar()` reads the right panel.
 */
export function DashboardShell({ shellTitle, leftSidebar, rightSidebar, contentProvider, children }: DashboardShellProps) {
  return (
    <TooltipProvider>
      <SidebarProvider keyboardShortcut={leftSidebar != null ? undefined : null}>
        <LeftSidebarProvider>
          {leftSidebar != null && (
            <Sidebar side="left" collapsible="icon">
              {leftSidebar}
              <SidebarRail />
            </Sidebar>
          )}
          <DashboardBody shellTitle={shellTitle} showLeftSidebar={leftSidebar != null} rightSidebar={rightSidebar} contentProvider={contentProvider}>
            {children}
          </DashboardBody>
        </LeftSidebarProvider>
      </SidebarProvider>
    </TooltipProvider>
  );
}

/**
 * Everything right of the left sidebar. It reads the left sidebar's state here, before the right sidebar's
 * provider shadows it, and passes it to the header's left toggle.
 */
function DashboardBody({ shellTitle, showLeftSidebar, rightSidebar, contentProvider: ContentProvider = Fragment, children }: Omit<DashboardShellProps, "leftSidebar"> & { showLeftSidebar: boolean }) {
  const left = useLeftSidebar();

  return (
    <SidebarProvider keyboardShortcut={null} className="min-w-0">
      <RightSidebarProvider><ContentProvider>
        <SidebarInset className="min-w-0">
          <DashboardHeader shellTitle={shellTitle} left={left} showLeftSidebar={showLeftSidebar} showRightSidebar={rightSidebar != null} />
          <div className="flex flex-1 flex-col gap-6 p-6">{children}</div>
        </SidebarInset>
        {rightSidebar != null && (
          <Sidebar side="right">
            {rightSidebar}
            <SidebarRail />
          </Sidebar>
        )}
      </ContentProvider></RightSidebarProvider>
    </SidebarProvider>
  );
}
