import { cn } from "@/lib/utils";

import { explorerFontClass } from "./explorer-fonts";

import "./explorer-tokens.css";

/** Stories only: the Explorer's background, type and colors around a part shown on its own. */
export function ExplorerStoryFrame({ children, padded = true }: { children: React.ReactNode; padded?: boolean }) {
  return (
    <div className={cn(explorerFontClass, "flex flex-col gap-7 bg-(--uncf-bg) text-[15px] text-(--uncf-ink)", padded && "p-6")}>
      {children}
    </div>
  );
}
