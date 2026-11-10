import { cn } from "@/lib/utils";

import { explorerFontClass } from "./explorer-fonts";
import { ExplorerHeader } from "./explorer-header";
import { explorerWrap } from "./explorer-styles";
import { ExplorerTabs } from "./explorer-tabs";

import "./explorer-tokens.css";

/** The Explorer's own app shell: the header and horizontal tabs from the design, then the current tab's page. */
export function ExplorerShell({ children }: { children: React.ReactNode }) {
  return (
    <div className={cn(explorerFontClass, "flex min-h-svh flex-col bg-(--uncf-bg) text-[15px] leading-normal text-(--uncf-ink)")}>
      <ExplorerHeader />
      <ExplorerTabs />
      <main className={cn(explorerWrap, "flex flex-1 flex-col gap-7 pt-10 pb-14")}>{children}</main>
    </div>
  );
}
