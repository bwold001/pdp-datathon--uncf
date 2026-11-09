import { type Dimension, isGatewayMeasure, type PathsResponse, type ResultRow, type ResultsResponse, type ResultStatus } from "@/app/(app)/uncf/data";

import { percentOf } from "./bars";
import { dimensionInfo, measureNames, valueLabel } from "./labels";

/** The shared result contract's columns, in order: every row carries its filters, status, definition and source. */
export const CSV_COLUMNS = [
  "cohort",
  "dimension",
  "group_value",
  "group",
  "measure",
  "measure_label",
  "pdp_name",
  "numerator",
  "denominator",
  "rate",
  "status",
  "status_label",
  "base",
  "n_left_out",
  "definition",
  "limitations",
  "source",
  "loaded_at",
  "data_label",
] as const;

const STATUS_LABEL: Record<ResultStatus, string> = {
  ok: "Shown",
  suppressed: "Hidden to protect privacy (fewer than 10 students)",
  not_yet_observable: "Not available yet",
  not_reported: "Not reported",
};

const SYNTHETIC = "SYNTHETIC";
const MOCK = "SYNTHETIC; MOCK (no year-2 paths API yet)";

type CsvRow = Record<(typeof CSV_COLUMNS)[number], string>;

/** The grouping as the saved results name it, e.g. "enrollment_intensity x pell" and "Full-time x Y". */
function groupColumns(group: ResultRow["group"], groupBy: Dimension[]): { dimension: string; value: string; label: string } {
  if (Object.keys(group).length === 0) return { dimension: "all", value: "all", label: "All students" };
  const sorted = [...groupBy].sort();
  return {
    dimension: sorted.join(" x "),
    value: sorted.map((dimension) => group[dimension] ?? "").join(" x "),
    label: groupBy.map((dimension) => `${dimensionInfo[dimension].label}: ${valueLabel(dimension, group[dimension] ?? "")}`).join("; "),
  };
}

/** One row; a hidden or missing number is blank with its status, never 0. */
function csvRow(fields: Omit<CsvRow, "rate" | "numerator" | "denominator">, numerator: number | null, denominator: number | null, shown: boolean): CsvRow {
  const ok = shown && numerator !== null && denominator !== null && denominator > 0;
  return {
    ...fields,
    numerator: ok ? String(numerator) : "",
    denominator: ok ? String(denominator) : "",
    // Four places, from the counts, so it matches the shown percent when rounded to one decimal.
    rate: ok ? (percentOf(numerator as number, denominator as number) / 100).toFixed(4) : "",
  };
}

/** Every outcome row for the view, then the year-2 paths and the college-type split (mock). */
export function buildCsvRows(outcomes: ResultsResponse[], paths: PathsResponse | null): CsvRow[] {
  const rows: CsvRow[] = [];
  for (const response of outcomes) {
    const { meta } = response;
    const isGateway = isGatewayMeasure(meta.measure);
    for (const row of response.rows) {
      const group = groupColumns(row.group, meta.group_by);
      const status = row.status;
      rows.push(
        csvRow(
          {
            cohort: meta.cohort,
            dimension: group.dimension,
            group_value: group.value,
            group: group.label,
            measure: meta.measure,
            measure_label: measureNames[meta.measure],
            pdp_name: meta.definition.pdp_name,
            status,
            status_label: STATUS_LABEL[status] + (status === "ok" && meta.provisional ? " (year 2 still arriving)" : ""),
            base: isGateway ? "students required to take it" : "students who entered",
            n_left_out: row.n_excluded === null ? "" : String(row.n_excluded),
            definition: meta.definition.what,
            limitations: meta.definition.limits.join(" | "),
            source: meta.source,
            loaded_at: meta.loaded_at,
            data_label: SYNTHETIC,
          },
          row.numerator,
          row.denominator,
          status === "ok",
        ),
      );
    }
  }
  if (!paths) return rows;

  const { meta } = paths;
  for (const row of paths.rows) {
    const group = groupColumns(row.group, meta.group_by);
    const base = {
      cohort: meta.cohort,
      dimension: group.dimension,
      group_value: group.value,
      group: group.label,
      pdp_name: "Built from PDP retention and persistence flags",
      n_left_out: "",
      source: meta.source,
      loaded_at: meta.loaded_at,
      data_label: MOCK,
    };
    const shown = row.status === "ok";
    const paths3: [string, string, number | null][] = [
      ["year2_path_returned_here", "Year-2 path: returned here", row.returned_here],
      ["year2_path_moved", "Year-2 path: moved to another college", row.moved],
      ["year2_path_no_enrollment", "Year-2 path: no enrollment found", row.no_enrollment],
    ];
    for (const [measure, label, count] of paths3) {
      rows.push(
        csvRow(
          {
            ...base,
            measure,
            measure_label: label,
            status: row.status,
            status_label: STATUS_LABEL[row.status],
            base: "students who entered",
            definition: "Where each entering student was in their second academic year. Each student is on one path.",
            limitations: "Mock: no API serves these paths yet; definitions and hiding are a proposal.",
          },
          count,
          row.students,
          shown,
        ),
      );
    }
    const splitShown = shown && row.college_type !== null;
    const types: [string, string, keyof NonNullable<typeof row.college_type>][] = [
      ["moved_college_type_four_year", "Moved to: 4-year college", "four_year"],
      ["moved_college_type_two_year", "Moved to: 2-year college", "two_year"],
      ["moved_college_type_not_on_record", "Moved to: type not on record", "not_on_record"],
    ];
    for (const [measure, label, key] of types) {
      rows.push(
        csvRow(
          {
            ...base,
            measure,
            measure_label: label,
            status: splitShown ? "ok" : "suppressed",
            status_label: splitShown ? STATUS_LABEL.ok : STATUS_LABEL.suppressed,
            base: "students who moved to another college",
            definition: "Type of the most recent other college on record, for students who moved.",
            limitations: "The most recent college on record can be after year 2. Mock: no API serves this yet.",
          },
          splitShown ? (row.college_type as NonNullable<typeof row.college_type>)[key] : null,
          row.moved,
          splitShown,
        ),
      );
    }
  }
  return rows;
}

/** The rows as CSV text, quoting any value with a comma, quote or line break. */
export function toCsvText(rows: CsvRow[]): string {
  const escape = (value: string) => (/[",\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value);
  return [CSV_COLUMNS.join(","), ...rows.map((row) => CSV_COLUMNS.map((column) => escape(row[column])).join(","))].join("\n");
}

/** A file name that says what's inside and that it's synthetic, e.g. explorer_entered-2022-23_by-pell_SYNTHETIC.csv. */
export function csvFileName(cohort: string, groupBy: Dimension[]): string {
  return `student-success_entered-${cohort}_by-${groupBy.join("-and-").replace(/_/g, "-")}_SYNTHETIC.csv`;
}

/** Save text as a file in the browser. */
export function downloadText(fileName: string, text: string): void {
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
