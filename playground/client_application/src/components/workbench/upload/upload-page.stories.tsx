import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { WorkbenchStorybookWrapper } from "@/components/testing/workbench-storybook-wrapper";
import { blockingCheckResults, mockCheckResults, mockSavedTables, mockUploadedFiles, uploadStepLabels } from "@/components/testing/upload-fixtures";
import { UploadPage } from "@/components/workbench/upload/upload-page";

const meta = {
  component: UploadPage,
  title: "Workbench/Upload/Upload page",
  args: {
    stage: "choose",
    steps: { steps: uploadStepLabels, currentStep: 0 },
    dropzone: { onFiles: fn(), onUseMockFiles: fn() },
    onRejectedFiles: fn(),
    files: { files: mockUploadedFiles },
    checks: { results: mockCheckResults, onFieldClick: fn(), onSave: fn(), onStartOver: fn() },
    saved: { tables: mockSavedTables, exploreHref: "#explore" },
  },
  decorators: [(Story, { args }) => (
    <WorkbenchStorybookWrapper page="upload" hasData={args.stage === "saved"}>
      <Story />
    </WorkbenchStorybookWrapper>
  )],
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof UploadPage>;
export default meta;
type Story = StoryObj<typeof meta>;

export const ChooseFiles: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Upload AR files" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Use the mock files" }));
    await expect(args.dropzone.onUseMockFiles).toHaveBeenCalledOnce();
  },
};
export const RejectedFile: Story = {
  name: "Rejected text file reaches the page callback",
  play: async ({ args, canvasElement }) => {
    const file = new File(["synthetic notes"], "notes.txt", { type: "text/plain" });
    const transfer = new DataTransfer();
    transfer.items.add(file);
    canvasElement.querySelector('[data-slot="empty"]')!.dispatchEvent(
      new DragEvent("drop", { bubbles: true, cancelable: true, dataTransfer: transfer }),
    );
    await expect(args.onRejectedFiles).toHaveBeenCalledWith([file]);
    await expect(args.dropzone.onFiles).not.toHaveBeenCalled();
  },
};
export const Checking: Story = {
  args: { stage: "checking", steps: { steps: uploadStepLabels, currentStep: 1 }, files: { files: mockUploadedFiles.map((file) => ({ ...file, status: "checking" })) } },
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText("Checking…")).toHaveLength(2);
    await expect(canvas.queryByRole("button", { name: "Save to database" })).not.toBeInTheDocument();
  },
};
export const Checked: Story = {
  args: { stage: "checked", steps: { steps: uploadStepLabels, currentStep: 1 } },
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Pell_Status_First_Year" }));
    await expect(args.checks.onFieldClick).toHaveBeenCalledWith("Pell_Status_First_Year");
    await userEvent.click(canvas.getByRole("button", { name: "Save to database" }));
    await expect(args.checks.onSave).toHaveBeenCalledOnce();
    await userEvent.click(canvas.getByRole("button", { name: "Start over" }));
    await expect(args.checks.onStartOver).toHaveBeenCalledOnce();
  },
};
export const Blocked: Story = {
  args: { stage: "checked", checks: { ...meta.args.checks, results: blockingCheckResults } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Save to database" })).toBeDisabled();
  },
};
export const Saving: Story = {
  args: { stage: "checked", checks: { ...meta.args.checks, saving: true } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Saving…" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Start over" })).toBeDisabled();
  },
};
export const Saved: Story = {
  args: { stage: "saved", steps: { steps: uploadStepLabels, currentStep: 3 }, files: { files: mockUploadedFiles.map((file) => ({ ...file, status: "saved" })) } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Saved" })).toBeVisible();
    await expect(canvas.getByRole("link", { name: "Explore the data" })).toHaveAttribute("href", "#explore");
  },
};
export const CheckRefused: Story = {
  args: { error: "notes.xlsx: choose CSV files only." },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("alert")).toHaveTextContent("choose CSV files only");
    await expect(canvas.getByRole("button", { name: "Choose files" })).toBeEnabled();
  },
};
export const SaveRefused: Story = {
  args: { stage: "checked", error: "The server could not save these files. Try again." },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("alert")).toHaveTextContent("could not save");
    await expect(canvas.getByRole("button", { name: "Save to database" })).toBeEnabled();
  },
};
export const Mobile: Story = {
  args: Checked.args,
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Upload AR files" })).toBeVisible();
    const document = canvasElement.ownerDocument.documentElement;
    await expect(document.scrollWidth).toBeLessThanOrEqual(document.clientWidth);
  },
};
