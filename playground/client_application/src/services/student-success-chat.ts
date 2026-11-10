/** Mirrors the UNCF analytics and chat transport contracts. */
import { apiRequest } from "@/lib/api-client";

export type AnalysisRequest = {
  analysis: "graduation" | "retention" | "enrollment";
  cohort?: string | null;
  credential?: "B" | "A" | "C" | null;
  program?: string | null;
};
export type CalculationRow = {
  label: string;
  kind: "rate" | "composition" | "count";
  group: Record<string, string>;
  horizon: "four_year" | "six_year" | "to_date" | null;
  status: "ok" | "suppressed" | "unknown" | "unavailable" | "not_yet_observable" | "provisional";
  numerator: number | null;
  denominator: number | null;
  count: number | null;
  rate: number | null;
  exclusions: Record<string, number>;
  calculation: string;
  note: string;
};
export type AnalysisReceipt = {
  analysis: AnalysisRequest["analysis"];
  parameters: AnalysisRequest;
  definition: { name: string; version: string; formula: string; population: string; grain: string; exclusions: string; limitations: string[] };
  rows: CalculationRow[];
  source: "synthetic";
  loaded_at: string | null;
  source_stamp: string | null;
  cutoff: string | null;
  coverage_provenance: string;
  academic_years: string[];
  program_definition: string;
  attribution: string;
  limitations: string[];
};
export type Clarification = {
  field: "cohort" | "credential" | "program";
  message: string;
  choices: { value: string; label: string }[];
  pending: AnalysisRequest;
};
export type ChatRequest = {
  prompt: string;
  proposals?: AnalysisRequest[];
  confirmed?: AnalysisRequest[];
  pending?: AnalysisRequest;
  selection?: { field: Clarification["field"]; value: string };
};
export type ChatResponse = {
  status: "answer" | "clarification" | "confirmation" | "unsupported";
  message: string;
  proposals?: AnalysisRequest[];
  receipts: AnalysisReceipt[];
  clarification: Clarification | null;
  source: "synthetic";
};

/** Use the configured Playground API origin; credentials stay on the server. */
export function sendStudentSuccessQuestion(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/chat", { method: "POST", json: request, timeoutMs: 90_000 });
}

/** Describe the complete supported scope using typed parameters, never generated prose. */
export function describeScope(scope: AnalysisRequest): string {
  if (scope.analysis === "retention") return `Retention for the complete ${scope.cohort} entering cohort, overall and by entry major.`;
  if (scope.analysis === "enrollment") return "Distinct enrollment by ethnicity and academic program for the latest two certified complete academic years, across all entering cohorts.";
  const credential = { B: "bachelor's degree", A: "associate degree", C: "certificate" }[scope.credential ?? "B"];
  const program = scope.program === "chemistry_family" ? "Chemistry family (40.05)" : "Chemistry, General (40.0501)";
  return `Graduation for the ${scope.cohort} entering cohort, ${credential}, ${program}; all four-year, six-year and completion-to-date perspectives.`;
}
