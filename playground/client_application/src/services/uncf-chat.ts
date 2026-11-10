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
  pending?: AnalysisRequest;
  selection?: { field: Clarification["field"]; value: string };
};
export type ChatResponse = {
  status: "answer" | "clarification" | "unsupported";
  message: string;
  receipts: AnalysisReceipt[];
  clarification: Clarification | null;
  source: "synthetic";
};

/** Use the configured Playground API origin; credentials stay on the server. */
export function sendUncfQuestion(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/uncf/chat", { method: "POST", json: request, timeoutMs: 90_000 });
}
