"use client";

import { ArrowLeft, Check, Printer, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";

import { loadResults, measures, type Cohort, type Dimension, type Measure, type ResultsQuery, type ResultsResponse } from "@/app/(app)/uncf/data";
import { LoadError } from "@/components/load-error";
import { Skeleton } from "@/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { selectedToggle } from "@/components/uncf/explorer/explorer-controls";
import { cohortLabel, dimensionInfo, measureNames } from "@/components/uncf/explorer/labels";
import { useApiResource } from "@/hooks/use-api-resource";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

import { buildCard } from "./card-model";
import { InsightCard } from "./insight-card";
import { checkTakeaway, MAX_TAKEAWAY } from "./takeaway-checks";

// Print only the card, full size, on one Letter page. The app's sidebar and top bar stay on screen only.
const PRINT_CSS = `
@media print {
  @page { size: letter; margin: 0; }
  body * { visibility: hidden !important; }
  .uncf-print-card, .uncf-print-card * { visibility: visible !important; }
  .uncf-print-scale { transform: none !important; }
  .uncf-print-card { position: fixed; left: 0; top: 0; box-shadow: none !important; }
}`;

type CardMakerProps = {
  cohort: Cohort;
  groupBy: Dimension[];
  initialMeasure: Measure;
  load?: (query: ResultsQuery) => Promise<ResultsResponse>;
};

/** Make a one-page insight card from an Explorer view: pick the outcome, write one checked sentence, save as PDF. */
export function CardMaker({ cohort, groupBy, initialMeasure, load = loadResults }: CardMakerProps) {
  const [measure, setMeasure] = useState<Measure>(initialMeasure);
  // One draft per outcome, so switching tabs never throws away a typed sentence.
  const [drafts, setDrafts] = useState<Partial<Record<Measure, string>>>({});
  const loader = useMemo(() => () => load({ measure, cohort, groupBy }), [load, measure, cohort, groupBy]);
  const { resource, retry } = useApiResource(loader);
  const viewText = `Students by ${groupBy.map((dimension) => dimensionInfo[dimension].phrase).join(" and ")}, entered ${cohortLabel(cohort)}`;
  const explorerHref = routes.uncfExplorer;

  return (
    <div className="flex flex-col gap-6">
      <style>{PRINT_CSS}</style>
      <Link href={explorerHref} className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" aria-hidden /> Back to the Explorer
      </Link>

      <div className="grid items-start gap-6 xl:grid-cols-[24rem_minmax(0,1fr)]">
        <section aria-label="Card settings" className="flex flex-col gap-6 rounded-2xl border bg-card p-5 sm:p-6">
          <div className="flex flex-col gap-2.5">
            <h2 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">1 · What the card shows</h2>
            <p className="rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm dark:border-indigo-900 dark:bg-indigo-950/40">
              <strong className="font-semibold">{viewText}</strong>
              <br />
              <span className="text-muted-foreground">From your Explorer view: every group, plus all students.</span>
            </p>
            <ToggleGroup
              aria-label="Outcome on the card"
              multiple={false}
              value={[measure]}
              onValueChange={(values) => {
                const next = measures.find((value) => value === values[0]);
                if (next) setMeasure(next);
              }}
              variant="outline"
              className="max-w-full flex-wrap"
            >
              {measures.map((value) => (
                <ToggleGroupItem key={value} value={value} className={selectedToggle}>
                  {measureNames[value]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </div>

          {resource.status === "success" ? (
            <TakeawayEditor
              response={resource.data}
              draft={drafts[measure]}
              onDraftChange={(text) => setDrafts((current) => ({ ...current, [measure]: text }))}
              onReset={() => setDrafts((current) => ({ ...current, [measure]: undefined }))}
            />
          ) : (
            <Skeleton className="h-64 rounded-xl" />
          )}
        </section>

        <section aria-label="Card preview" className="flex min-w-0 flex-col items-center gap-3 rounded-2xl bg-muted/60 p-6">
          <p className="text-xs text-muted-foreground">Live preview · exactly what prints</p>
          {resource.status === "loading" && <Skeleton className="h-[739px] w-full max-w-[571px] rounded-md" />}
          {resource.status === "error" && <LoadError title="This card couldn't load." message={resource.message} onRetry={retry} className="min-h-56" />}
          {resource.status === "success" && <CardPreview response={resource.data} takeaway={drafts[measure]} />}
        </section>
      </div>
    </div>
  );
}

/** The takeaway box, its checks, and the save button that waits until the checks pass. */
function TakeawayEditor({ response, draft, onDraftChange, onReset }: { response: ResultsResponse; draft: string | undefined; onDraftChange: (text: string) => void; onReset: () => void }) {
  const content = buildCard(response);
  const text = draft ?? content.suggested;
  const checks = checkTakeaway(text, content.facts);
  const failing = checks.filter((check) => !check.passed).length;
  const blocked = failing > 0;
  return (
    <>
      <div className="flex flex-col gap-2.5">
        <h2 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
          <label htmlFor="takeaway">2 · The one-sentence takeaway</label>
        </h2>
        <textarea
          id="takeaway"
          value={text}
          onChange={(event) => onDraftChange(event.target.value)}
          rows={4}
          placeholder="Quote at least one rate from the card."
          aria-describedby="takeaway-count takeaway-checks"
          className="w-full resize-y rounded-xl border border-foreground/40 bg-background px-3.5 py-3 text-[15px] leading-relaxed focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
        />
        <div className="flex items-center justify-between gap-2">
          <button type="button" onClick={onReset} className="rounded-md border px-2.5 py-1.5 text-xs font-medium hover:bg-muted">
            Use the suggested sentence
          </button>
          <span id="takeaway-count" className={cn("text-xs tabular-nums", text.length > MAX_TAKEAWAY ? "text-red-700" : "text-muted-foreground")}>
            {text.length} of {MAX_TAKEAWAY} characters
          </span>
        </div>
        <ul id="takeaway-checks" aria-label="Checks before sharing" aria-live="polite" className="flex flex-col gap-2">
          {checks.map((check) => (
            <li key={check.id} className="flex items-start gap-2 text-sm">
              <span aria-hidden className={cn("mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full text-white", check.passed ? "bg-green-700" : "bg-amber-700")}>
                {check.passed ? <Check className="size-3" strokeWidth={3} /> : <TriangleAlert className="size-2.5" strokeWidth={3} />}
              </span>
              <span>
                <span className="sr-only">{check.passed ? "Passed: " : "Needs a fix: "}</span>
                <strong className="font-semibold">{check.label}</strong> <span className="text-muted-foreground">{check.note}</span>
              </span>
            </li>
          ))}
        </ul>
        <p className="text-xs text-muted-foreground">The checks catch common slips. Read the sentence once more before you share it.</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          aria-disabled={blocked}
          aria-describedby="save-reason"
          onClick={() => {
            if (!blocked) window.print();
          }}
          className={cn(
            "inline-flex h-11 items-center gap-2 rounded-lg px-4 text-sm font-medium",
            blocked ? "cursor-not-allowed bg-muted text-muted-foreground" : "bg-foreground text-background hover:opacity-90",
          )}
        >
          <Printer className="size-4" aria-hidden /> Save as PDF
        </button>
        <span id="save-reason" className={cn("text-xs font-medium", blocked ? "text-amber-800 dark:text-amber-300" : "text-green-800 dark:text-green-300")}>
          {blocked ? `Fix ${failing} ${failing === 1 ? "check" : "checks"} to save` : "Ready: choose “Save as PDF” in the print dialog"}
        </span>
      </div>
    </>
  );
}

/** The card at 70% for the preview; printing shows it at full size. */
function CardPreview({ response, takeaway }: { response: ResultsResponse; takeaway: string | undefined }) {
  const content = buildCard(response);
  const loadedAt = new Date(response.meta.loaded_at);
  const loadedText = Number.isNaN(loadedAt.getTime())
    ? response.meta.loaded_at
    : loadedAt.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
  return (
    <div className="h-[739px] w-[571px] max-w-full overflow-hidden rounded-md bg-white shadow-[0_1px_2px_rgba(10,10,11,0.06),0_24px_48px_-16px_rgba(30,27,75,0.28)]">
      <div className="uncf-print-scale origin-top-left scale-[0.7]">
        <div className="uncf-print-card">
          <InsightCard content={content} takeaway={takeaway ?? content.suggested} source={response.meta.source} loadedAt={loadedText} />
        </div>
      </div>
    </div>
  );
}
