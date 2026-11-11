/** Application-owned v2 wire types; results never use provider prose. */
import { apiRequest } from "@/lib/api-client";

export type Choice = { value: string | number; label: string };
export type Unresolved = { unresolved: true; question: string; choices: Choice[] };
export type Parameter = string | number | string[] | Record<string, string | null> | Unresolved;
export type Step = { step_id: string; kind: "defined_measure" | "legacy_analysis"; operation_id: string; depends_on: string[]; parameters: Record<string, Parameter> };
export type Plan = { kind: "proposed" | "executable"; catalog_version: string; snapshot_ref: string; steps: Step[] };
export type Exclusion = { reason: string; count: number };
export type Status = "ok" | "provisional" | "suppressed" | "unknown" | "unavailable" | "not_yet_observable" | "not_reported";
export type Rate = { numerator: number; denominator: number; value: number; numerator_unit: string; denominator_unit: string; n_students?: number | null; n_excluded?: number | null; n_out_of_scope?: number | null; split?: Record<string, number> | null };
export type Breakdown = { status: Status; group: Record<string, string | null>; exclusions?: Exclusion[] } & Partial<Rate>;
export type TableRow = { status: Status; cells?: (string | number | null)[]; path?: string | null };
export type Payload =
  | ({ kind: "rate"; breakdowns: Breakdown[] } & Rate)
  | { kind: "count"; count: number; unit: string }
  | { kind: "mean"; value: number; n: number; unit: string }
  | { kind: "correlation"; coefficient: number; n: number; method: string; x_unit: string; y_unit: string }
  | { kind: "mean_comparison"; unit: string; groups: { id: string; mean: number; n: number }[]; differences: { minuend: string; subtrahend: string; value: number }[] }
  | { kind: "table"; columns: { id: string; type: string; unit: string }[]; rows: TableRow[]; pages?: { rows: TableRow[] }[] };
export type Receipt = {
  schema_version: 2; step_id: string; request: Step; operation_id: string; operation_version: string;
  disclosure_profile?: { id: string; version: string };
  population: string; grain: string; time_window: string; definitions: { id: string; version: string }[];
  assumptions: string[]; limitations: string[]; baseline_changes: string[];
  source: { label: "synthetic"; snapshot_ref: string; fingerprint: string; loaded_at: string; coverage: string };
  versions: { catalog: string; pipeline: string; configuration: string; coverage: string; implementation: string; disclosure: string; features: { id: string; version: string }[]; method?: { id: string; version: string } | null };
  computation_fingerprint: string; execution_id: string; started_at: string; completed_at: string;
  result: { status: Status; payload?: Payload; reason?: string; exclusions?: Exclusion[] };
};
export type Clarification = { step_id: string; parameter: string; question: string; choices: Choice[] };
export type Issue = { code: string; step_id: string | null; message: string };
export type ChatResponseV2 = {
  protocol_version: 2; status: "clarification" | "confirmation" | "answer" | "unsupported" | "error";
  plan: Plan | null; outcome: "complete" | "partial" | "failed" | null;
  step_outcomes: { step_id: string; outcome: "completed" | "failed" | "not_executed"; issue: Issue | null }[];
  clarification: Clarification | null; receipts: Receipt[]; issues: Issue[]; message: string;
};
export type ChatRequestV2 = { protocol_version: 2; prompt: string; plan?: Plan; selection?: { step_id: string; parameter: string; value: string | number }; confirmed?: Plan };

/** Send explicit v2 requests while preserving legacy transport as a separate service. */
export function sendStudentSuccessV2(request: ChatRequestV2): Promise<ChatResponseV2> {
  return apiRequest<ChatResponseV2>("/chat", { method: "POST", json: request, timeoutMs: 90_000 });
}
