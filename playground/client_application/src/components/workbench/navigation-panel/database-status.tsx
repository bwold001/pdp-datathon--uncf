import { DatabaseIcon } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export type DatabaseState =
  | { status: "empty" }
  | { status: "loaded"; tables: [string, ...string[]] }
  | { status: "loading" }
  | { status: "unavailable" };

function describeDatabase(state: DatabaseState) {
  switch (state.status) {
    case "empty": return "Empty · no files yet";
    case "loaded": return `${state.tables.length} ${state.tables.length === 1 ? "table" : "tables"} · ${state.tables.join(", ")}`;
    case "loading": return "Checking local database…";
    case "unavailable": return "Unavailable · could not connect";
  }
}

/** Prop-driven status, usable anywhere. It never reads database or sidebar state. */
export function DatabaseStatus({ state, compact = false }: { state: DatabaseState; compact?: boolean }) {
  const description = describeDatabase(state);
  if (compact) {
    return <div role="status" aria-label={`Local database: ${description}`} title={`Local database: ${description}`} className="flex size-8 items-center justify-center">
      <DatabaseIcon aria-hidden="true" className="size-4" />
    </div>;
  }
  return (
    <Card size="sm" role="status" aria-label="Local database">
      <CardHeader>
        <CardTitle><p className="flex items-center gap-2">
          <span aria-hidden="true" className={cn("size-2 shrink-0 rounded-full", state.status === "loaded" ? "bg-primary" : "bg-muted-foreground")} />
          Local database
        </p></CardTitle>
        <CardDescription><p>{description}</p></CardDescription>
      </CardHeader>
    </Card>
  );
}
