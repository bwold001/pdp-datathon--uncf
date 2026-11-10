import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, waitFor } from "storybook/test";
import type { AnalysisReceipt, ChatRequest, ChatResponse } from "@/services/uncf-chat";
import { UncfChat } from "./chat";
import { CalculationCard } from "./calculation-card";

const receipt: AnalysisReceipt = {
  analysis: "retention", parameters: { analysis: "retention", cohort: "2022-23" },
  definition: { name: "Retention overall and by entry program", version: "1", formula: "retained students / students with known outcomes", population: "Selected entry cohort", grain: "Student and cohort", exclusions: "Unknown retention outcomes", limitations: [] },
  rows: [{ label: "Retention — All majors", kind: "rate", group: {}, horizon: null, status: "ok", numerator: 20, denominator: 40, rate: .5, count: null, exclusions: { unknown_outcome: 0 }, calculation: "20 / 40 = 50.00%", note: "Known outcomes only." }],
  source: "synthetic", loaded_at: "2026-06-30", source_stamp: "synthetic-fixture", cutoff: "2026-06-30", coverage_provenance: "Story fixture only", academic_years: [], program_definition: "", attribution: "Entry major uses first-term program", limitations: ["Synthetic fixture, not a real campus result."],
};
const response: ChatResponse = { status: "answer", message: "Results and calculation details are below.", receipts: [receipt], clarification: null, source: "synthetic" };

const meta = {
  component: UncfChat,
  title: "UNCF/Student success chat",
  args: { request: fn<(payload: ChatRequest) => Promise<ChatResponse>>(async () => response) },
  decorators: [(Story) => <div className="mx-auto h-[44rem] max-w-3xl border"><Story /></div>],
  parameters: { layout: "padded", docs: { description: { component: "Bounded student-success questions, explicit clarification and calculation evidence. Stories use invented interface fixtures; integration tests exercise the real normalized database." } } },
} satisfies Meta<typeof UncfChat>;
export default meta;
type Story = StoryObj<typeof meta>;

export const AskAndInspectCalculation: Story = {
  play: async ({ canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Your question" }), "Retention for 2022-23?");
    await userEvent.click(canvas.getByRole("button", { name: /^Send$/ }));
    await expect(canvas.getByText("50.00%", { exact: true })).toBeVisible();
    await expect(canvas.getByText("20 / 40 = 50.00%")).toBeVisible();
    await userEvent.click(canvas.getByText("How these results were calculated"));
    await expect(canvas.getByText("retained students / students with known outcomes")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Start over" }));
    await expect(canvas.queryByText("50.00%", { exact: true })).not.toBeInTheDocument();
  },
};

export const ClarifyCohort: Story = {
  args: { request: fn(async (payload: ChatRequest): Promise<ChatResponse> => payload.selection ? response : {
    status: "clarification", source: "synthetic", message: "Which entry cohort?", receipts: [],
    clarification: { field: "cohort", message: "Which entry cohort?", pending: { analysis: "retention" }, choices: [{ value: "2022-23", label: "2022-23" }] },
  }) },
  play: async ({ canvas, userEvent, args }) => {
    await userEvent.click(canvas.getByRole("button", { name: "What is the retention rate for all majors?" }));
    await userEvent.click(canvas.getByRole("button", { name: /^2022-23$/ }));
    await expect(canvas.getByText("50.00%", { exact: true })).toBeVisible();
    await expect(args.request).toHaveBeenLastCalledWith({ prompt: "2022-23", pending: { analysis: "retention" }, selection: { field: "cohort", value: "2022-23" } });
  },
};

export const ProviderFailure: Story = {
  args: { request: fn<(payload: ChatRequest) => Promise<ChatResponse>>(async () => { throw new Error("Provider is unavailable"); }) },
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "What is the retention rate for all majors?" }));
    await expect(canvas.getByRole("alert")).toHaveTextContent("Provider is unavailable");
    await expect(canvas.getByRole("textbox", { name: "Your question" })).toBeEnabled();
  },
};

export const ResetWhilePending: Story = {
  play: async ({ canvas, userEvent, args }) => {
    let resolve!: (value: ChatResponse) => void;
    const lateReply = new Promise<ChatResponse>((done) => { resolve = done; });
    (args.request as typeof meta.args.request).mockReturnValueOnce(lateReply);
    await userEvent.click(canvas.getByRole("button", { name: "What is the retention rate for all majors?" }));
    await expect(canvas.getByRole("status")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Start over" }));
    resolve(response);
    await waitFor(() => expect(canvas.queryByRole("status")).not.toBeInTheDocument());
    await expect(canvas.queryByText("50.00%", { exact: true })).not.toBeInTheDocument();
  },
};

export const DistinctOutcomeStates: Story = {
  render: () => <CalculationCard receipt={{ ...receipt, rows: [
    { ...receipt.rows[0], label: "Zero result", numerator: 0, denominator: 40, rate: 0, calculation: "0 / 40 = 0.00%" },
    ...(["suppressed", "unknown", "unavailable", "not_yet_observable"] as const).map((status) => ({ ...receipt.rows[0], label: status, status, numerator: null, denominator: null, rate: null, exclusions: {}, calculation: "" })),
  ] }} />,
  play: async ({ canvas }) => {
    await expect(canvas.getByText("0.00%", { exact: true })).toBeVisible();
    for (const label of ["Suppressed", "Unknown", "Unavailable", "Not yet observable"]) {
      await expect(canvas.getByText(label, { exact: true })).toBeVisible();
    }
  },
};

export const LongAnswerStaysInView: Story = {
  play: async ({ canvas, userEvent, args }) => {
    let resolve!: (value: ChatResponse) => void;
    const lateReply = new Promise<ChatResponse>((done) => { resolve = done; });
    (args.request as typeof meta.args.request).mockReturnValueOnce(lateReply);
    await userEvent.click(canvas.getByRole("button", { name: "What is the retention rate for all majors?" }));
    await expect(canvas.getByRole("status")).toBeVisible();
    resolve({ ...response, receipts: [{ ...receipt, rows: Array.from({ length: 20 }, (_, index) => ({ ...receipt.rows[0], label: `Program ${index}` })) }] });
    await expect(canvas.getByText("Program 19")).toBeInTheDocument();
    const scrollingRegion = canvas.getByRole("list", { name: "Conversation" }).parentElement!;
    await waitFor(() => expect(scrollingRegion.scrollTop).toBeGreaterThan(0));
  },
};
