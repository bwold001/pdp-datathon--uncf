import type { Metadata } from "next";
import { notFound } from "next/navigation";

// The (dashboard) route group keeps this page out of sandbox/layout.tsx: DashboardShell fills the viewport,
// so it can't sit inside PageShell's header and footer.
// The Dashboard borrows the Charts example's charts. If you rewrite chart-examples, give the Dashboard its own
// charts first, or this page breaks with it.
import { Charts } from "@/app/(app)/sandbox/chart-examples/charts";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { SandboxNavigation } from "@/components/sandbox/sandbox-navigation";
import { SidebarGroupContent } from "@/components/ui/sidebar";
import { env } from "@/lib/env";

export const metadata: Metadata = {
  title: "Example: a dashboard",
  description: "The sandbox charts inside DashboardShell, with navigation on the left and a context panel on the right.",
};

export default function SandboxDashboardPage() {
  if (!env.sandboxEnabled) notFound();

  return (
    <DashboardShell shellTitle="Dashboard" leftSidebar={<SandboxNavigation />} rightSidebar={<Details />}>
      <Charts />
    </DashboardShell>
  );
}

function Details() {
  return (
    <DashboardSidebar title="Details" label="About this data">
      <SidebarGroupContent className="flex flex-col gap-2 px-2 text-muted-foreground">
        <p>Every chart is built from synthetic PDP data, not real students.</p>
        <p>Put filters or details for the selected chart here.</p>
      </SidebarGroupContent>
    </DashboardSidebar>
  );
}
