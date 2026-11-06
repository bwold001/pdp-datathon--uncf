import type { FieldIndexSection } from "@/components/workbench/field-guide/field-index";
import type { CheckResult } from "@/components/workbench/upload/check-results-list";
import type { SavedTable } from "@/components/workbench/upload/upload-saved-callout";
import type { DatabaseState } from "@/components/workbench/navigation-panel/database-status";
import type { GuideField } from "@/components/workbench/shared/dictionary-types";
import type { ColumnDefinition, LoadSummary, TableSummary, SourceKind, Upload } from "@/services/workbench";

/** "table.column": the same key the loader uses for a field. */
export function fieldId(column: Pick<ColumnDefinition, "table" | "column">) {
  return `${column.table}.${column.column}`;
}

/** One dictionary column as the field guide and context panel show it. */
export function toGuideField(column: ColumnDefinition): GuideField {
  const sources = column.sources.map((source) => `${source.source_file}: ${source.source_column}`);
  const description = column.description ?? column.sources[0]?.lookup_description ?? "No description in the data dictionary.";
  return {
    id: fieldId(column),
    title: column.dictionary_name ?? column.column,
    description: column.notes ? `${description}\n\n${column.notes}` : description,
    source: sources.length > 0 ? sources.join(", ") : "Not filled from a cohort or course file",
    values: column.dictionary_values.map((value) => ({ code: value.code, meaning: value.meaning ?? "" })),
    group: column.table,
    file: column.sources[0]?.source_file ?? column.table,
  };
}


/** Cohort and course rows that failed checks or were held back: what Home counts as warnings. */
export function warningCount(summary: LoadSummary | null): number {
  // The cohort and course files share the load's validation run; the repo's enrichment files each have their own.
  const failed = Object.values(summary?.validation ?? {})
    .filter((counts) => counts.run_id === summary?.run_id)
    .reduce((total, counts) => total + counts.rows_failed, 0);
  return failed + (summary?.held_back_rows ?? 0);
}


/** Tables that hold rows now. */
export function loadedTables(tables: TableSummary[]): TableSummary[] {
  return tables.filter((table) => (table.row_count ?? 0) > 0);
}

// Enrichment tables come from repo files and fill on every load, so only student rows mean data is loaded.
const STUDENT_TABLE = "student";

/** True when the student table holds rows. */
export function hasStudentRows(tables: TableSummary[]): boolean {
  return (tables.find((table) => table.name === STUDENT_TABLE)?.row_count ?? 0) > 0;
}

/** The navigation sidebar's database status, from the table list's load state. */
export function databaseState(tables: TableSummary[] | "loading" | "error"): DatabaseState {
  if (tables === "loading") return { status: "loading" };
  if (tables === "error") return { status: "unavailable" };
  if (!hasStudentRows(tables)) return { status: "empty" };
  const [first, ...rest] = loadedTables(tables).map((table) => table.name);
  return { status: "loaded", tables: [first, ...rest] };
}

/** The raw file each source kind stands for, as the dictionary's sources name it. */
const SOURCE_FILES: Record<SourceKind, string> = {
  cohort: "pdp_cohort_data.csv",
  course: "pdp_course_data.csv",
};

export const KIND_LABELS: Record<SourceKind, string> = { cohort: "Cohort", course: "Course" };


/** The column names in a CSV's first line, without quotes or a byte-order mark. */
export function parseHeader(firstLine: string): string[] {
  return firstLine
    .replace(/^\uFEFF/, "")
    .split(",")
    .map((name) => name.trim().replace(/^"(.*)"$/, "$1"))
    .filter((name) => name.length > 0);
}

/** Read a file's header without loading the whole file. */
export async function readHeader(file: File): Promise<string[]> {
  const start = await file.slice(0, 64 * 1024).text();
  return parseHeader(start.split(/\r?\n/, 1)[0] ?? "");
}

/** Every column the dictionary says a source file has. */
function sourceColumns(columns: ColumnDefinition[], kind: SourceKind): Set<string> {
  return new Set(
    columns.flatMap((column) => column.sources.filter((s) => s.source_file === SOURCE_FILES[kind]).map((s) => s.source_column)),
  );
}

/**
 * Whether a file looks like the cohort or the course file. Shared columns such as Student_GUID
 * don't count, so it's whichever file's own columns the header has more of. On a tie the file
 * name decides, if it says "cohort" or "course"; otherwise null.
 */
export function detectKind(header: string[], columns: ColumnDefinition[], fileName = ""): SourceKind | null {
  const cohortColumns = sourceColumns(columns, "cohort");
  const courseColumns = sourceColumns(columns, "course");
  const cohort = header.filter((name) => cohortColumns.has(name) && !courseColumns.has(name)).length;
  const course = header.filter((name) => courseColumns.has(name) && !cohortColumns.has(name)).length;
  if (cohort !== course) return cohort > course ? "cohort" : "course";

  const name = fileName.toLowerCase();
  if (name.includes("cohort") && !name.includes("course")) return "cohort";
  if (name.includes("course") && !name.includes("cohort")) return "course";
  return null;
}

/** The check results for one stored upload: recognized, plus any columns the loader ignores. */
export function uploadResults(upload: Upload, columnCount: number): CheckResult[] {
  const label = KIND_LABELS[upload.kind].toLowerCase();
  const results: CheckResult[] = [
    {
      id: `${upload.upload_id}-ok`,
      severity: "ok",
      title: `${upload.filename}: recognized as a ${label} file`,
      detail: `${columnCount} columns, and every column the loader reads is there.`,
    },
  ];
  const unexpected = upload.unexpected_columns;
  if (unexpected.length > 0) {
    results.push({
      id: `${upload.upload_id}-unexpected`,
      severity: "info",
      title: `${unexpected.length} ${unexpected.length === 1 ? "column isn't" : "columns aren't"} read`,
      detail: `The loader ignores ${unexpected.join(", ")}.`,
    });
  }
  return results;
}

/** A check result for a file that couldn't be stored, carrying the reason. */
export function uploadErrorResult(fileName: string, message: string): CheckResult {
  return { id: `${fileName}-error`, severity: "error", title: `${fileName} can't be saved`, detail: message };
}

/** The plain-language lines a finished load's summary adds to the Saved callout. */
export function summaryLines(summary: LoadSummary | null): string[] {
  if (!summary) return [];
  const lines: string[] = [];
  for (const [file, counts] of Object.entries(summary.validation ?? {})) {
    const failed = counts.rows_failed > 0 ? `, ${counts.rows_failed.toLocaleString("en-US")} failed checks` : "";
    lines.push(`${file}: ${counts.rows_read.toLocaleString("en-US")} rows read${failed}.`);
  }
  const fixes = Object.entries(summary.fixes ?? {}).filter(([, count]) => count > 0);
  if (fixes.length > 0) {
    lines.push(`Fixed on the way in: ${fixes.map(([name, count]) => `${name.replaceAll("_", " ")} (${count.toLocaleString("en-US")})`).join(", ")}.`);
  }
  if (summary.held_back_rows) {
    lines.push(`${summary.held_back_rows.toLocaleString("en-US")} rows were held back because they link to a record that isn't there.`);
  }
  return lines;
}


/** "Loading… done: map, fix." from a running load's progress lines, which start with the step name. */
export function progressNote(progress: string[]): string {
  const steps = progress.map((line) => line.split(":", 1)[0]);
  return steps.length > 0 ? `Loading… done: ${steps.join(", ")}.` : "Loading…";
}

/** The loaded tables, from a run summary's row counts. */
export function savedTablesFromSummary(summary: LoadSummary | null): SavedTable[] {
  return Object.entries(summary?.tables ?? {}).map(([name, rowCount]) => ({ name, rowCount }));
}


/** Fields grouped into one index section per table, keeping the schema's order. */
export function toIndexSections(fields: GuideField[]): FieldIndexSection[] {
  const sections = new Map<string, FieldIndexSection>();
  for (const field of fields) {
    const section = sections.get(field.group) ?? { id: field.group, label: field.group, fields: [] };
    section.fields.push({ id: field.id, title: field.title, notInData: field.notInData, fillPercent: field.profile?.fillPercent });
    sections.set(field.group, section);
  }
  return [...sections.values()];
}

