import { useId, type ComponentProps } from "react";
import { ToolCard } from "@/components/workbench/home/tool-card";

export type TeamTool = ComponentProps<typeof ToolCard> & { id: string };

/** Lists the tools registered by project teams under a shared section heading. */
export function TeamToolsSection({ tools }: { tools: TeamTool[] }) {
  const headingId = useId();
  return (
    <section aria-labelledby={headingId} className="flex flex-col gap-3">
      <header className="flex flex-col gap-1">
        <h2 id={headingId} className="text-lg font-medium">Team tools</h2>
        <p className="text-sm text-muted-foreground">
          Each project team adds its feature here as a card. Cards open the team&apos;s own page.
        </p>
      </header>
      <ul className="grid gap-3 sm:grid-cols-3">
        {tools.map(({ id, ...tool }) => (
          <li key={id}>
            <ToolCard {...tool} />
          </li>
        ))}
      </ul>
    </section>
  );
}
