import { useId } from "react";
import { CircleAlert, CircleCheck, CircleX, Info } from "lucide-react";
import { cn } from "cn";

import { Button } from "@/components/ui/button";
import { Item, ItemActions, ItemContent, ItemDescription, ItemMedia, ItemTitle } from "@/components/ui/item";
import { Spinner } from "@/components/ui/spinner";

/** "error" blocks saving; the others are things to know before saving. */
export type CheckSeverity = "ok" | "warning" | "info" | "error";

export type CheckResult = {
  id: string;
  severity: CheckSeverity;
  title: string;
  /** One plain-language sentence or two on what was found and what happens to it. */
  detail: string;
  /** The field the result is about, as a column code such as "Pell_Status_First_Year". */
  fieldId?: string;
};

type CheckResultsListProps = {
  results: CheckResult[];
  /** Opens the field's definition, such as useContextPanel().openField. */
  onFieldClick?: (fieldId: string) => void;
  onSave: () => void;
  onStartOver: () => void;
  /** True while the save is running. */
  saving?: boolean;
};

const severityIcon = {
  ok: { Icon: CircleCheck, label: "Passed" },
  warning: { Icon: CircleAlert, label: "Warning" },
  info: { Icon: Info, label: "Note" },
  error: { Icon: CircleX, label: "Blocks saving" },
} satisfies Record<CheckSeverity, { Icon: React.ElementType; label: string }>;

/** "Nothing blocks saving. 5 things to know first.", or how many problems block it. */
function summaryText(results: CheckResult[]) {
  const errors = results.filter((result) => result.severity === "error").length;
  if (errors > 0) return `${errors} ${errors === 1 ? "problem blocks" : "problems block"} saving.`;
  const notes = results.filter((result) => result.severity === "warning" || result.severity === "info").length;
  if (notes === 0) return "Nothing blocks saving.";
  return `Nothing blocks saving. ${notes} ${notes === 1 ? "thing" : "things"} to know first.`;
}

/** One check result: what was found, and a button to the field it's about. */
function CheckResultRow({ result, onFieldClick, fieldHintId }: { result: CheckResult; onFieldClick?: (fieldId: string) => void; fieldHintId: string }) {
  const { Icon, label } = severityIcon[result.severity];
  const { fieldId } = result;
  return (
    <Item size="sm" data-severity={result.severity}>
      <ItemMedia variant="icon" className={cn(result.severity === "error" && "text-destructive")}>
        <Icon aria-hidden />
        <span className="sr-only">{label}: </span>
      </ItemMedia>
      <ItemContent>
        <ItemTitle className="line-clamp-none">{result.title}</ItemTitle>
        <ItemDescription className="line-clamp-none">{result.detail}</ItemDescription>
      </ItemContent>
      {fieldId && onFieldClick && (
        <ItemActions>
          <Button variant="ghost" size="sm" className="font-mono" aria-describedby={fieldHintId} onClick={() => onFieldClick(fieldId)}>
            {fieldId}
          </Button>
        </ItemActions>
      )}
    </Item>
  );
}

/** The upload check's findings, then the buttons to save or start over. Saving is off while any error remains. */
export function CheckResultsList({ results, onFieldClick, onSave, onStartOver, saving = false }: CheckResultsListProps) {
  const headingId = useId();
  const fieldHintId = useId();
  const blocked = results.some((result) => result.severity === "error");
  return (
    <section aria-labelledby={headingId} className="flex flex-col gap-4">
      <header className="flex flex-col gap-1">
        <h2 id={headingId} className="text-lg font-medium">
          {summaryText(results)}
        </h2>
        {onFieldClick && results.some((result) => result.fieldId) && (
          <p id={fieldHintId} className="text-sm text-muted-foreground">Click a field to see its definition.</p>
        )}
      </header>
      <ul className="flex flex-col">
        {results.map((result) => (
          <li key={result.id}>
            <CheckResultRow result={result} onFieldClick={onFieldClick} fieldHintId={fieldHintId} />
          </li>
        ))}
      </ul>
      <div className="flex flex-wrap gap-2">
        <Button size="lg" onClick={onSave} disabled={blocked || saving}>
          {saving && <Spinner aria-hidden />}
          {saving ? "Saving…" : "Save to database"}
        </Button>
        <Button size="lg" variant="outline" onClick={onStartOver} disabled={saving}>
          Start over
        </Button>
      </div>
    </section>
  );
}
