import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, waitFor } from "storybook/test";
import { loadSuggestedQuestions, type ChatRequestV2, type ChatResponseV2, type Payload, type Receipt, type SuggestedQuestion } from "@/services/student-success-v2";
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
  args: { loadSuggestions: async (): Promise<SuggestedQuestion[]> => [], request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (payload): Promise<ChatResponseV2> => payload.confirmed ? response : base) },
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
    await expect(canvas.getByText(/a − b: -2 credits/)).toBeInTheDocument();
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

export const ExplorationMissingMeans: Story = {
  render: () => <Evidence payload={{ kind: "mean_comparison", unit: "credits", groups: [
    { id: "zero", mean: 20, n: 2, count: 3, missing_count: 1 },
    { id: "one_to_two", mean: null, n: 0, count: 1, missing_count: 1 },
    { id: "three_plus", mean: 5, n: 1, count: 1, missing_count: 0 },
  ], differences: [
    { minuend: "one_to_two", subtrahend: "zero", value: null, minuend_n: 0, subtrahend_n: 2, unavailable_reason: "missing_group_mean" },
    { minuend: "three_plus", subtrahend: "zero", value: -15, minuend_n: 1, subtrahend_n: 2 },
  ] }} />,
  play: async ({ canvas }) => {
    await expect(canvas.getByText("zero: 20 credits · n=2 · missing=1")).toBeInTheDocument();
    await expect(canvas.getByText("one_to_two: Unavailable — no observed credits · n=0 · missing=1")).toBeInTheDocument();
    await expect(canvas.getByText("three_plus − zero: -15 credits · n=1 versus n=2")).toBeInTheDocument();
    await expect(canvas.getByText(/Unavailable — missing group mean/)).toBeInTheDocument();
  },
};

const chemistryStep = { step_id: "graduation", kind: "legacy_analysis" as const, operation_id: "legacy.graduation", depends_on: [], parameters: { cohort: "2022-23", credential: "B", program: "chemistry_family" } };
const chemistryPlan = { ...plan, steps: [chemistryStep] };
const chemistryReceipt: Receipt = {
  ...receipt, step_id: "graduation", request: chemistryStep, operation_id: "legacy.graduation",
  presentation: {
    title: "Graduation results", scope: "2022-23 entry cohort · Bachelor's degree · Chemistry family (40.05)",
    summary: "A graduation rate isn't available for this selection.",
    items: ["Within four years: We haven't verified how long the data follows these students.", "Within six years: We haven't verified how long the data follows these students.", "Completion to date: We haven't verified how long the data follows these students."],
    caveats: ["An unavailable rate does not mean that nobody graduated or that the rate is 0%.", "Graduation specifically in Chemistry requires award-program information that is missing from this extract."],
  },
  result: { status: "ok", payload: { kind: "table", columns: [{ id: "label", type: "text", unit: "perspective" }], rows: [
    { status: "not_yet_observable", explanation: { label: "Entrants completing in any program", kind: "rate", horizon: "four_year", reason: "followup_not_verified", note: "Whole-cohort follow-up is not certified for this horizon." } },
    { status: "unavailable", explanation: { label: "Entrants completing in any program", kind: "rate", horizon: "to_date", reason: "followup_not_verified", note: "Extract cutoff and cohort follow-up must be declared." } },
  ] } },
};
const retentionSuggestion = { operation_id: "retention.rate", question: "What is the school retention rate?", availability: "not_checked" as const, explanation: "We'll check whether the selected students have usable information when you calculate." };

export const ChemistryExplanation: Story = {
  render: () => <EvidenceCard receipt={chemistryReceipt} />,
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByText("A graduation rate isn't available for this selection.")).toBeVisible();
    await expect(canvas.getByText(/2022-23 entry cohort/)).toBeVisible();
    await expect(canvas.getByText(/does not mean that nobody graduated/)).toBeVisible();
    await expect(canvas.queryByText("Available", { exact: true })).not.toBeInTheDocument();
    await expect(canvas.getByRole("table", { hidden: true })).not.toBeVisible();
    await userEvent.click(canvas.getByText("Calculation details — all groups and supporting counts"));
    await expect(canvas.getByRole("table")).toBeVisible();
    await expect(canvas.getByText(/Whole-cohort follow-up is not certified/)).toBeVisible();
  },
};

export const ChemistryClarifyConfirmAndExplore: Story = {
  args: {
    loadSuggestions: async () => [{ ...retentionSuggestion, operation_id: "legacy.graduation", question: "What is the graduation rate for chemistry majors?" }],
    request: fn<(payload: ChatRequestV2) => Promise<ChatResponseV2>>(async (payload) => {
      if (payload.prompt === retentionSuggestion.question) return base;
      if (payload.confirmed) return { ...response, plan: chemistryPlan, receipts: [chemistryReceipt], step_outcomes: [{ step_id: "graduation", outcome: "completed", issue: null }], suggestions: [retentionSuggestion] };
      const parameters = { ...chemistryStep.parameters } as Record<string, string | { unresolved: true; question: string; choices: { value: string; label: string }[] }>;
      const chosen = payload.plan?.steps[0].parameters ?? {};
      const fields = [
        { key: "cohort", question: "Which entry cohort?", value: "2022-23", label: "2022-23" },
        { key: "credential", question: "Which credential?", value: "B", label: "Bachelor's degree" },
        { key: "program", question: "Which program definition?", value: "chemistry_family", label: "Chemistry family" },
      ];
      let pending: typeof fields[number] | undefined;
      for (const field of fields) {
        const value = payload.selection?.parameter === field.key ? payload.selection.value : chosen[field.key];
        if (typeof value === "string") parameters[field.key] = value;
        else { parameters[field.key] = { unresolved: true, question: field.question, choices: [{ value: field.value, label: field.label }] }; pending ??= field; }
      }
      if (pending) return { ...base, status: "clarification", plan: { ...chemistryPlan, kind: "proposed", steps: [{ ...chemistryStep, parameters }] }, clarification: { step_id: "graduation", parameter: pending.key, question: pending.question, choices: [{ value: pending.value, label: pending.label }] } };
      return { ...base, plan: chemistryPlan, guidance: [{ step_id: "graduation", state: "known_limitation", message: "Graduation rates are unavailable because we haven't verified how long the data follows this entry cohort." }], suggestions: [retentionSuggestion] };
    }),
  },
  play: async ({ canvas, userEvent, args }) => {
    await userEvent.click(await canvas.findByRole("button", { name: "What is the graduation rate for chemistry majors?" }));
    await userEvent.click(canvas.getByRole("button", { name: "2022-23" }));
    await userEvent.click(canvas.getByRole("button", { name: "Bachelor's degree" }));
    await userEvent.click(canvas.getByRole("button", { name: "Chemistry family" }));
    await expect(canvas.getByText(/Graduation rates are unavailable because/)).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Confirm scope and calculate" })).toBeDisabled();
    await userEvent.click(canvas.getByRole("checkbox"));
    await userEvent.click(canvas.getByRole("button", { name: "Confirm scope and calculate" }));
    await expect(canvas.getByText("A graduation rate isn't available for this selection.")).toBeVisible();
    await expect(args.request).toHaveBeenLastCalledWith({ protocol_version: 2, prompt: "What is the graduation rate for chemistry majors?", confirmed: chemistryPlan });
    await userEvent.click(canvas.getByText("Explore another question"));
    await userEvent.click(canvas.getByRole("button", { name: retentionSuggestion.question }));
    await expect(args.request).toHaveBeenLastCalledWith({ protocol_version: 2, prompt: retentionSuggestion.question });
    await expect(canvas.getByRole("checkbox")).not.toBeChecked();
    await expect(canvas.getByRole("button", { name: "Confirm scope and calculate" })).toBeDisabled();
  },
};

export const SuggestionsUnavailable: Story = {
  args: { loadSuggestions: async () => { throw new Error("Metadata unavailable"); } },
  play: async ({ canvas }) => {
    await expect(await canvas.findByText(/Suggested questions couldn't be loaded/)).toBeVisible();
    await expect(canvas.getByRole("textbox", { name: "Your question" })).toBeEnabled();
  },
};

export const CatalogSuggestionsOnly: Story = {
  args: { loadSuggestions: async () => [retentionSuggestion] },
  play: async ({ canvas, userEvent, args }) => {
    await expect(await canvas.findByRole("button", { name: retentionSuggestion.question })).toBeVisible();
    await expect(canvas.queryByRole("button", { name: /graduation rate for chemistry/ })).not.toBeInTheDocument();
    await expect(canvas.getByText(retentionSuggestion.explanation)).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: retentionSuggestion.question }));
    await expect(args.request).toHaveBeenLastCalledWith({ protocol_version: 2, prompt: retentionSuggestion.question });
    await expect(canvas.getByRole("checkbox")).not.toBeChecked();
  },
};


export const CatalogSuggestionRequest: Story = {
  args: { loadSuggestions: loadSuggestedQuestions },
  beforeEach: () => {
    const originalFetch = globalThis.fetch;
    globalThis.fetch = fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      if (input === `${env.apiBaseUrl}/uncf/analysis-v2/catalog`) {
        return new Response(JSON.stringify({ suggestions: [retentionSuggestion] }), {
          status: 200, headers: { "Content-Type": "application/json" },
        });
      }
      return originalFetch(input, init);
    });
    return () => { globalThis.fetch = originalFetch; };
  },
  play: async ({ canvas }) => {
    await expect(await canvas.findByRole("button", { name: retentionSuggestion.question })).toBeVisible();
    await expect(globalThis.fetch).toHaveBeenCalledWith(
      `${env.apiBaseUrl}/uncf/analysis-v2/catalog`,
      expect.objectContaining({ cache: "no-store" }),
    );
  },
};
