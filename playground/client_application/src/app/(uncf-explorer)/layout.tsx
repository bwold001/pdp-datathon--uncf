import { ExplorerShell } from "@/components/uncf/layout/explorer-shell";

/**
 * Every Explorer tab, in its own shell: the header and horizontal tabs replace the app's left sidebar, as in the
 * team design. It sits outside (app) for that reason, like the workbench's (dashboard) group.
 */
export default function ExplorerLayout({ children }: { children: React.ReactNode }) {
  return <ExplorerShell>{children}</ExplorerShell>;
}
