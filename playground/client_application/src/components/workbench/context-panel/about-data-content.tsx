import { TermList } from "@/components/workbench/shared/term-list";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import type { DescribedItem } from "@/components/workbench/shared/dictionary-types";

export type AboutDataContentProps = {
  introduction: string;
  hasData: boolean;
  terms: DescribedItem[];
  caveats?: DescribedItem[];
  filterExplanations?: DescribedItem[];
};

/** Semantic sections independent of sidebar, routing, and shared state. */
export function AboutDataContent({ introduction, hasData, terms, caveats = [], filterExplanations = [] }: AboutDataContentProps) {
  return (
    <div className="flex flex-col gap-4">
      <header className="flex flex-col gap-2">
        <p className="text-sm text-muted-foreground">Context</p>
        <h2 className="font-semibold">About this data</h2>
        <p className="text-sm">{introduction}</p>
      </header>
      {filterExplanations.length > 0 && <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Your filters, explained</h3>
        <TermList terms={filterExplanations} />
      </section>}
      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Key terms</h3>
        <TermList terms={terms} />
      </section>
      {/* Static caveats: role="note" so the Alert doesn't announce on every render. */}
      {hasData && caveats.length > 0 && <Alert role="note">
        <AlertTitle><h3>Watch out for</h3></AlertTitle>
        <AlertDescription><TermList terms={caveats} /></AlertDescription>
      </Alert>}
    </div>
  );
}
