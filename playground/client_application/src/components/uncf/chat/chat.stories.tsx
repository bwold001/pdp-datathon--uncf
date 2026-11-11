import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, waitFor } from "storybook/test";
import type { ChatRequestV2, ChatResponseV2, Payload, Receipt } from "@/services/student-success-v2";
import { StudentSuccessChat } from "./chat";
import { Evidence, EvidenceCard } from "./evidence-card";
import StudentSuccessChatPage from "@/app/(uncf-explorer)/uncf/chat/page";
import { env } from "@/lib/env";

const step = { step_id: "dfw", kind: "defined_measure" as const, operation_id: "dfw.rate", depends_on: [], parameters: { cohort: "2023-24", filters: { pell: "Y" }, group_by: [] } };
const plan = { kind: "executable" as const, catalog_version: "2", snapshot_ref: "a".repeat(64), steps: [step] };
const receipt: Receipt = {
  schema_version: 2, step_id: "dfw", request: step, operation_id: "dfw.rate", operation_version: "1",
  disclosure_profile: { id: "dashboard_v1", version: "2" },
  population: "Pell entry cohort with classifiable final grades", grain: "Course enrollment", time_window: "All observed terms",
  definitions: [{ id: "dfw.rate", version: "1" }], assumptions: [], limitations: [], baseline_changes: [],
  source: { label: "synthetic", snapshot_ref: "a".repeat(64), fingerprint: "b".repeat(64), loaded_at: "2026-11-11T00:00:00Z", coverage: "Story fixture only" },
  versions: { catalog: "2", pipeline: "story", implementation: "story-build", configuration: "story-config", coverage: "story", disclosure: "2", features: [] },
  computation_fingerprint: "c".repeat(64), execution_id: "story-run", started_at: "2026-11-11T00:00:00Z", completed_at: "2026-11-11T00:00:01Z",
  result: { status: "ok", payload: { kind: "rate", value: .5, numerator: 1, denominator: 2, numerator_unit: "DFW enrollments", denominator_unit: "classifiable enrollments", n_students: 1, n_excluded: 1, breakdowns: [] }, exclusions: [{ reason: "unknown_grade", count: 1 }] },
};
const base: ChatResponseV2 = { protocol_version: 2, status: "confirmation", message: "Review the complete explicit scope before execution.", plan, outcome: null, step_outcomes: [], clarification: null, receipts: [], issues: [] };
const response: ChatResponseV2 = { ...base, status: "answer", message: "Synthetic results below.", outcome: "complete", step_outcomes: [{ step_id: "dfw", outcome: "completed", issue: null }], receipts: [receipt] };
const meta = {
  component: StudentSuccessChat, title: "UNCF/Student success chat",
  args: { request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (payload): Promise<ChatResponseV2> => payload.confirmed ? response : base) },
  decorators: [(Story) => <div className="mx-auto h-[44rem] max-w-3xl border"><Story /></div>],
  parameters: { layout: "padded" },
} satisfies Meta<typeof StudentSuccessChat>;
export default meta;
type Story = StoryObj<typeof meta>;

export const AskAndInspectCalculation: Story = {
  play: async ({ canvas, userEvent, args }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Pell DFW?");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByRole("button", { name: "Confirm scope and calculate" })).toBeDisabled();
    await userEvent.click(canvas.getByRole("checkbox", { name: /I confirm this scope/ }));
    await userEvent.click(canvas.getByRole("button", { name: "Confirm scope and calculate" }));
    await expect(canvas.getByText("50.00%", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Distinct students n=1")).toBeVisible();
    await expect(args.request).toHaveBeenLastCalledWith({ protocol_version: 2, prompt: "Pell DFW?", confirmed: plan });
  },
};
export const ResetWhilePending: Story = {
  play: async ({ canvas, userEvent, args }) => {
    let resolve!: (value: ChatResponseV2) => void;
    (args.request as typeof meta.args.request).mockReturnValueOnce(new Promise((done) => { resolve = done; }));
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Old question");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await userEvent.click(canvas.getByRole("button", { name: "Start over" }));
    resolve(response);
    await waitFor(() => expect(canvas.queryByRole("status")).not.toBeInTheDocument());
    await expect(canvas.queryByText("50.00%", { exact: true })).not.toBeInTheDocument();
  },
};
export const NewQuestionInvalidatesPending: Story = {
  play: async ({ canvas, userEvent, args }) => {
    let resolve!: (value: ChatResponseV2) => void;
    (args.request as typeof meta.args.request).mockReturnValueOnce(new Promise((done) => { resolve = done; }));
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Old question");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "New question");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByRole("checkbox")).toBeVisible();
    resolve(response);
    await waitFor(() => expect(canvas.queryByText("50.00%", { exact: true })).not.toBeInTheDocument());
  },
};
export const SmallGroupsAndZero: Story = {
  render: () => <div>{Array.from({ length: 9 }, (_, i) => <EvidenceCard key={i} receipt={{ ...receipt, result: { status: "ok", payload: { kind: "rate", value: 0, numerator: 0, denominator: i + 1, numerator_unit: "retained students", denominator_unit: "known outcomes", n_students: i + 1, n_excluded: 1, breakdowns: [] }, exclusions: [{ reason: "unknown", count: 1 }] } }} />)}</div>,
  play: async ({ canvas }) => {
    for (let n = 1; n <= 9; n++) await expect(canvas.getByText(`Distinct students n=${n}`, { exact: true })).toBeInTheDocument();
    await expect(canvas.getAllByText("0.00%", { exact: true })).toHaveLength(9);
  },
};
export const EveryPayloadAndHistoricalStatus: Story = {
  render: () => <div className="space-y-4">
    {([
      { kind: "count", count: 1, unit: "students" }, { kind: "mean", value: 2.5, n: 1, unit: "credits" },
      { kind: "mean_comparison", unit: "credits", groups: [{ id: "a", mean: 1, n: 1 }, { id: "b", mean: 3, n: 2 }], differences: [{ minuend: "a", subtrahend: "b", value: -2 }] },
      { kind: "correlation", coefficient: -1, n: 2, method: "pearson", x_unit: "enrollments", y_unit: "credits" },
      { kind: "table", columns: [{ id: "path", type: "text", unit: "label" }, { id: "n", type: "integer", unit: "students" }], rows: [{ status: "ok", cells: ["small comparison", 1] }] },
    ] satisfies Payload[]).map((payload, i) => <Evidence key={i} payload={payload} />)}
    {(["suppressed", "unknown", "unavailable", "not_yet_observable", "not_reported"] as const).map((status) => <EvidenceCard key={status} receipt={{ ...receipt, result: { status, reason: "no_evidence" } }} />)}
  </div>,
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/Pearson r=-1/)).toBeInTheDocument();
    await expect(canvas.getByText("a − b: -2 credits")).toBeInTheDocument();
    await expect(canvas.getByText(/Historical suppressed receipt/)).toBeInTheDocument();
  },
};
export const PartialAnswer: Story = {
  args: { request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (): Promise<ChatResponseV2> => ({ ...response, plan: { ...plan, steps: [step, { ...step, step_id: "tiers" }] }, outcome: "partial", step_outcomes: [...response.step_outcomes, { step_id: "tiers", outcome: "not_executed", issue: { step_id: "tiers", code: "timeout", message: "The query timed out." } }] })) },
  play: async ({ canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Two steps");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByRole("alert")).toHaveTextContent("Partial answer");
    await expect(canvas.getByText(/tiers: not_executed/)).toBeVisible();
  },
};
export const ImmutablePages: Story = {
  render: () => <Evidence payload={{ kind: "table", columns: [{ id: "component", type: "text", unit: "path" }, { id: "value", type: "integer", unit: "students" }], rows: Array.from({ length: 200 }, (_, i) => ({ status: "ok", cells: [`group[${i}]`, i] })), pages: [{ rows: [{ status: "ok", cells: ["group[200]", 1] }] }] }} />,
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Next evidence page" }));
    await expect(canvas.getByText("group[200]", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Page 2 of 2 · 201 rows")).toBeVisible();
  },
};

export const ClarifyWholePlan: Story = {
  args: { request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (payload): Promise<ChatResponseV2> => payload.selection ? base : {
    ...base, status: "clarification", plan: { ...plan, kind: "proposed", steps: [{ ...step, parameters: { ...step.parameters, cohort: { unresolved: true, question: "Which entry cohort?", choices: [{ value: "2023-24", label: "2023-24" }] } } }, { ...step, step_id: "tiers", operation_id: "credit_momentum.summary", parameters: { cohort: "2023-24", retention_type: "school", filters: { pell: "Y" } } }] },
    clarification: { step_id: "dfw", parameter: "cohort", question: "Which entry cohort?", choices: [{ value: "2023-24", label: "2023-24" }] },
  }) },
  play: async ({ canvas, userEvent, args }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Pell DFW and tiers?");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByText("tiers: credit_momentum.summary")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: /^2023-24$/ }));
    const sent = (args.request as typeof meta.args.request).mock.calls[1][0];
    await expect(sent.plan?.steps).toHaveLength(2);
    await expect(sent.plan?.steps[0].parameters.filters).toEqual({ pell: "Y" });
    await expect(sent.selection).toEqual({ step_id: "dfw", parameter: "cohort", value: "2023-24" });
  },
};
export const ProviderFailure: Story = {
  args: { request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async () => { throw new Error("Provider is unavailable"); }) },
  play: async ({ canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "DFW?");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByRole("alert")).toHaveTextContent("Provider is unavailable");
  },
};
export const StalePlanNeedsReview: Story = {
  args: { request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (payload): Promise<ChatResponseV2> => payload.confirmed ? { ...base, plan: { ...plan, snapshot_ref: "updated-snapshot" }, message: "The source changed. Review this updated scope before confirming again." } : base) },
  play: async ({ canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "DFW?");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await userEvent.click(canvas.getByRole("checkbox"));
    await userEvent.click(canvas.getByRole("button", { name: "Confirm scope and calculate" }));
    await expect(canvas.getByText(/The source changed/)).toBeVisible();
    await expect(canvas.getByRole("checkbox")).not.toBeChecked();
    await expect(canvas.getByRole("button", { name: "Confirm scope and calculate" })).toBeDisabled();
  },
};

export const ProviderFreeDeployment: Story = {
  beforeEach: () => {
    const descriptor = Object.getOwnPropertyDescriptor(env, "studentSuccessChatEnabled")!;
    Object.defineProperty(env, "studentSuccessChatEnabled", { ...descriptor, value: false });
    return () => { Object.defineProperty(env, "studentSuccessChatEnabled", descriptor); };
  },
  render: () => <StudentSuccessChatPage />,
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/Chat is not enabled on this site/)).toBeVisible();
    await expect(canvas.queryByRole("textbox", { name: "Your question" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: "Confirm scope and calculate" })).not.toBeInTheDocument();
  },
};
