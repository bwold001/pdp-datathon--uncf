"use client";

import { FlaskConicalIcon } from "lucide-react";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { SidebarNavMenu } from "@/components/layout/sidebar-nav-menu";
import { useSidebar } from "@/components/ui/sidebar";
import { sandboxNavItems } from "@/content/sandbox-examples";
import { routes } from "@/lib/routes";

/** The sandbox home, then every example from content/sandbox-examples.ts, so a new example appears here too. */
const items = [{ label: "Sandbox", href: routes.sandbox, icon: FlaskConicalIcon }, ...sandboxNavItems];

/** Client adapter keeps icons and sheet behavior out of the server page's props. */
export function SandboxNavigation() {
  const { isMobile, setOpenMobile } = useSidebar();
  return (
    <DashboardSidebar title="Playground" label="Sandbox">
      <SidebarNavMenu items={items} activeHref={routes.sandboxDashboard} label="Sandbox" onNavigate={() => { if (isMobile) setOpenMobile(false); }} />
    </DashboardSidebar>
  );
}
