import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { uploadStepLabels } from "@/components/testing/upload-fixtures";
import { UploadSteps } from "./upload-steps";

const meta = {
  component: UploadSteps, title: "Workbench/Upload/Upload steps",
  args: { steps: uploadStepLabels, currentStep: 0 },
} satisfies Meta<typeof UploadSteps>;
export default meta;
type Story = StoryObj<typeof meta>;

/** Before any file is chosen. */
export const ChoosingFiles: Story = {
  name: "Step 1: Choose files",
  play: async ({ canvas }) => {
    const steps = canvas.getAllByRole("listitem");
    await expect(steps[0]).toHaveAttribute("aria-current", "step");
    await expect(steps.map((step) => step.dataset.state)).toEqual(["current", "upcoming", "upcoming"]);
  },
};

/** Files are chosen and being checked, or the check results are showing. */
export const Checking: Story = {
  name: "Step 2: Check files",
  args: { currentStep: 1 },
  play: async ({ canvas }) => {
    const steps = canvas.getAllByRole("listitem");
    await expect(steps[0]).toHaveTextContent("Choose files (done)");
    await expect(steps[1]).toHaveAttribute("aria-current", "step");
  },
};

/** After the save, every step is done and none is current. */
export const Saved: Story = {
  name: "Step 3: Saved files",
  args: { currentStep: 3 },
  play: async ({ canvas }) => {
    const steps = canvas.getAllByRole("listitem");
    await expect(steps.map((step) => step.dataset.state)).toEqual(["done", "done", "done"]);
    await expect(canvas.queryByRole("listitem", { current: "step" })).toBeNull();
  },
};
