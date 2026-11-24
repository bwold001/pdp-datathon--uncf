import type { Payload, Receipt } from "@/services/student-success-v2";

const horizons = {
  four_year: "Within four years", six_year: "Within six years", to_date: "Completion to date",
};
const reasons: Record<string, string> = {
  empty_population: "No students match this selection.",
  missing_required_evidence: "Information needed to calculate this result is missing.",
  followup_not_verified: "We haven't verified how long the data follows these students.",
  insufficient_followup: "These students haven't been followed long enough to report this result.",
  no_known_outcomes: "The selected students do not have usable outcome information for this calculation.",
  completion_program_missing: "We cannot tell which program students graduated from because the necessary award information is missing.",
};
const groups: Record<string, string> = {
  zero: "0 observed online enrollments", one_to_two: "1–2 observed online enrollments",
  three_plus: "3+ observed online enrollments", retained: "Retained", not_retained: "Not retained",
};
type Table = Extract<Payload, { kind: "table" }>;

/** Read disclosed table cells by column name without changing the receipt or its values. */
function cellsFor(table: Table, cells: NonNullable<Table["rows"][number]["cells"]>) {
  return Object.fromEntries(table.columns.map((column, index) => [column.id, cells[index]]));
}

/** Keep each graduation perspective and horizon attached to its value or missing-evidence reason. */
function graduationItems(table: Table): string[] {
  const items: string[] = [];
  const seen = new Set<string>();
  for (const row of [...table.rows, ...(table.pages ?? []).flatMap((page) => page.rows)]) {
    if (row.explanation) {
      const detail = row.explanation;
      const identity = JSON.stringify([detail.horizon, detail.kind, detail.label, detail.reason]);
      if (seen.has(identity)) continue;
      seen.add(identity);
      const label = detail.horizon ? `${horizons[detail.horizon]} — ${detail.label}` : detail.label;
      items.push(`${label}: ${reasons[detail.reason] ?? detail.note ?? reasons.missing_required_evidence}`);
    } else if (row.cells && (row.status === "ok" || row.status === "provisional")) {
      const cells = cellsFor(table, row.cells);
      if (cells.kind === "exclusion" || typeof cells.label !== "string") continue;
      const window = horizons[cells.horizon as keyof typeof horizons];
      const label = window ? `${window} — ${cells.label}` : cells.label;
      if (typeof cells.rate === "number") {
        items.push(`${label}: ${(cells.rate * 100).toFixed(2)}% (${cells.numerator} of ${cells.denominator} students).`);
      }
    }
  }
  return items;
}

/** Describe each group's separate earned/attempted samples using already-calculated means. */
function groupedItems(table: Table): string[] {
  const items: string[] = [];
  for (const row of [...table.rows, ...(table.pages ?? []).flatMap((page) => page.rows)]) {
    if (!row.cells || (row.status !== "ok" && row.status !== "provisional")) continue;
    const cells = cellsFor(table, row.cells);
    if (typeof cells.group !== "string") continue;
    const label = groups[cells.group] ?? cells.group;
    for (const metric of ["earned", "attempted"] as const) {
      const mean = cells[`${metric}_mean`];
      const n = cells[`${metric}_n`];
      const missing = cells[`${metric}_missing`];
      const value = typeof mean === "number" ? `${mean} credits` : "Unavailable — no observed credits";
      items.push(`${label} — average first-year credits ${metric}: ${value} (usable n=${n}; missing=${missing}).`);
    }
  }
  return items;
}

/** Improve chat wording locally; dashboard screens and API presentation remain untouched. */
export function chatAnswerItems(receipt: Receipt): string[] {
  const table = receipt.result.payload;
  if (table?.kind === "table") {
    if (receipt.operation_id === "legacy.graduation") {
      const items = graduationItems(table);
      if (items.length > 0) return items;
    }
    if (receipt.operation_id === "grouped_summary") return groupedItems(table);
  }
  return receipt.presentation?.items ?? [];
}
