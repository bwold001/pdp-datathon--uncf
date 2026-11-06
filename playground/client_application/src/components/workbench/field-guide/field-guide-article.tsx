"use client";

import type { ReactNode } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CodeMeaningList } from "@/components/workbench/shared/code-meaning-list";
import { ValueDistribution } from "@/components/workbench/shared/value-distribution";
import type { GuideField } from "@/components/workbench/shared/dictionary-types";

/** Supports dictionary emphasis and code while keeping HTML and links as inert text. */
function inlineDescription(text: string) {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return (
      <strong key={index}>{part.slice(2, -2)}</strong>
    );
    if (part.startsWith("*") && part.endsWith("*")) return (
      <em key={index}>{part.slice(1, -1)}</em>
    );
    if (part.startsWith("`") && part.endsWith("`")) return (
      <code key={index}>{part.slice(1, -1)}</code>
    );
    return part;
  });
}

type FieldGuideArticleProps = {
  field?: GuideField;
  profileSource?: "mock" | "uploaded";
  filterAction?: { onClick: () => void };
  description?: ReactNode;
};

/** Shows the guide's field article independently of the context panel. */
export function FieldGuideArticle({ field, profileSource = "mock", filterAction, description }: FieldGuideArticleProps) {
  if (!field) return (
    <section className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold">Choose a field</h2>
      <p>Select a field to read its definition and values.</p>
    </section>
  );
  return (
    <article className="flex min-w-0 flex-col gap-5">
      <header className="flex flex-col gap-2">
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary">{field.group}</Badge>
          <Badge variant="outline">{field.file}</Badge>
        </div>
        <h2 className="text-xl font-semibold">{field.title}</h2>
        <p className="break-all text-sm">
          <code>{field.id}</code>
        </p>
      </header>
      <p className="whitespace-pre-line text-sm">{description ?? inlineDescription(field.description)}</p>
      {field.notInData && (
        <Alert role="note">
          <AlertTitle>Not in this data</AlertTitle>
          <AlertDescription>This field is documented but is not included in the supplied files.</AlertDescription>
        </Alert>
      )}
      {!!field.values?.length && (
        <section className="flex flex-col gap-3">
          <h3 className="font-medium">What the values mean</h3>
          <CodeMeaningList values={field.values} />
        </section>
      )}
      {!field.notInData && field.profile && (
        <Card>
          <CardHeader>
            <CardTitle>
              <h3>{profileSource === "mock" ? "In the mock data" : "In your data"}</h3>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ValueDistribution profile={field.profile} />
          </CardContent>
        </Card>
      )}
      {profileSource === "uploaded" && !field.notInData && filterAction && (
        <Button variant="outline" className="h-auto self-start whitespace-normal" onClick={filterAction.onClick}>
          Filter the data by this field
        </Button>
      )}
      <footer>
        <p className="break-words text-sm text-muted-foreground">Source: {field.source}</p>
      </footer>
    </article>
  );
}
