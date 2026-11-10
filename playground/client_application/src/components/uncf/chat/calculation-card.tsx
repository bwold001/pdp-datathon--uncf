import type { AnalysisReceipt, CalculationRow } from "@/services/uncf-chat";

const statuses: Record<CalculationRow["status"], string> = {
  ok: "Available", provisional: "Provisional", suppressed: "Suppressed",
  unknown: "Unknown", unavailable: "Unavailable", not_yet_observable: "Not yet observable",
};
const horizons = { four_year: "Four-year", six_year: "Six-year", to_date: "Completion to date" };

/** Show returned values only; hidden and missing outcomes never become a zero. */
function resultValue(row: CalculationRow) {
  if (row.status !== "ok" && row.status !== "provisional") return statuses[row.status];
  if (row.kind === "count") return row.count?.toLocaleString() ?? "Unavailable";
  return row.rate === null ? "Unknown" : `${(row.rate * 100).toFixed(2)}%`;
}

/** Render one shared-service receipt with its formula, evidence and limitations. */
export function CalculationCard({ receipt }: { receipt: AnalysisReceipt }) {
  return (
    <article className="min-w-0 rounded-xl border bg-card p-4 text-sm">
      <h3 className="font-semibold">{receipt.definition.name}</h3>
      <p className="mt-1 text-muted-foreground">
        {receipt.parameters.cohort && `Entry cohort: ${receipt.parameters.cohort}. `}
        {receipt.parameters.credential && `Credential: ${receipt.parameters.credential}. `}
        {receipt.program_definition}
        {receipt.academic_years.length > 0 && ` Academic years: ${receipt.academic_years.join(" and ")}.`}
      </p>
      <ul className="mt-4 space-y-3">
        {receipt.rows.map((row, index) => (
          <li key={index} className="rounded-lg bg-muted/40 p-3">
            <p className="font-medium">{row.horizon && `${horizons[row.horizon]} · `}{row.label}</p>
            {Object.keys(row.group).length > 0 && <p className="break-words text-muted-foreground">{Object.entries(row.group).map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`).join(" · ")}</p>}
            <p className="mt-1 text-lg font-semibold tabular-nums">{resultValue(row)}</p>
            {row.status === "provisional" && <p className="text-amber-700 dark:text-amber-400">Provisional: follow-up is incomplete.</p>}
            {row.kind === "composition" && <p className="text-muted-foreground">Graduate composition, not a graduation rate.</p>}
            {row.calculation && <p className="mt-1 font-mono text-xs">{row.calculation}</p>}
            {row.note && <p className="mt-1 text-muted-foreground">{row.note}</p>}
            {Object.entries(row.exclusions).map(([reason, count]) => <p key={reason} className="text-xs text-muted-foreground">Excluded — {reason.replaceAll("_", " ")}: {count}</p>)}
          </li>
        ))}
      </ul>
      <details className="mt-4">
        <summary className="cursor-pointer font-medium">How these results were calculated</summary>
        <dl className="mt-3 space-y-2 break-words">
          {[
            ["Formula", receipt.definition.formula], ["Population", receipt.definition.population],
            ["Grain", receipt.definition.grain], ["Exclusion policy", receipt.definition.exclusions],
            ["Program attribution", receipt.attribution], ["Extract cutoff", receipt.cutoff ?? "Not certified"],
            ["Source loaded", receipt.loaded_at ?? "Unavailable"], ["Coverage", receipt.coverage_provenance],
            ["Definition version", receipt.definition.version],
          ].map(([label, value]) => <div key={label}><dt className="font-medium">{label}</dt><dd className="text-muted-foreground">{value}</dd></div>)}
        </dl>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-muted-foreground">
          {receipt.limitations.map((note) => <li key={note}>{note}</li>)}
        </ul>
      </details>
      <p className="mt-3 text-xs text-muted-foreground">Synthetic demonstration data. These are not findings about real students or institutions.</p>
    </article>
  );
}
