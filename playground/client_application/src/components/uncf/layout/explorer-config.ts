import { routes } from "@/lib/routes";

/** The header's words. */
export const explorerHeader = {
  title: "Student Persistence and Pathway Explorer",
  source: "Source: PDP Analysis-Ready files",
  sampleBadge: "Sample data · illustrative values",
  exportLabel: "Export PDF · PNG · CSV",
};

/** One tab: a page under the Explorer shell. */
export type ExplorerTab = { label: string; href: string };

// Tab order, left to right. A new tab is a page folder under (uncf-explorer)/uncf/ plus a line here.
export const explorerTabs: ExplorerTab[] = [
  { label: "Student paths", href: routes.uncfPaths },
  { label: "DFW", href: routes.uncfDfw },
  { label: "Gateway courses", href: routes.uncfGateway },
  { label: "Credit momentum", href: routes.uncfCreditMomentum },
];
