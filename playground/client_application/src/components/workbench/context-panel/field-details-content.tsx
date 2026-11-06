"use client";

import { ArrowLeftIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CodeMeaningList } from "@/components/workbench/shared/code-meaning-list";
import { ValueDistribution } from "@/components/workbench/shared/value-distribution";
import type { FieldDefinition } from "@/components/workbench/shared/dictionary-types";

/** Dictionary content can be composed in a sidebar or a field guide. */
export function FieldDetailsContent({ field, onBack }: { field?: FieldDefinition; onBack?: () => void }) {
  return (
    <div className="flex flex-col gap-4">
      <header className="flex flex-col gap-2">
        {onBack && <Button variant="ghost" className="self-start" onClick={onBack}><ArrowLeftIcon data-icon="inline-start" />About this data</Button>}
        {field && <p className="break-all text-sm"><code>{field.id}</code></p>}
        <h2 className="font-semibold">{field?.title ?? "Field unavailable"}</h2>
      </header>
      <p className="text-sm">{field?.description ?? "This field is not in the supplied dictionary. Return to About this data to choose another field."}</p>
      {!!field?.values?.length && <section className="flex flex-col gap-3">
        <h3 className="text-sm font-medium">What the values mean</h3>
        <CodeMeaningList values={field.values} compact />
      </section>}
      {field?.profile && <section className="flex flex-col gap-3">
        <h3 className="text-sm font-medium">In your data</h3>
        <ValueDistribution profile={field.profile} compact />
      </section>}
      {field && <footer><p className="break-words text-sm text-muted-foreground">Source: {field.source}</p></footer>}
    </div>
  );
}
