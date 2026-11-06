import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { StepNumber } from "./step-number";

const meta = {
  component: StepNumber, title: "Components/UI/Step number",
  args: { children: 1 },
} satisfies Meta<typeof StepNumber>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Decorative number at default size",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("1")).toHaveAttribute("data-size", "default");
    await expect(canvas.getByText("1")).toHaveAttribute("aria-hidden", "true");
  },
};

/** Sits beside a line of text, as in BuildSteps. */
export const Small: Story = {
  args: { size: "sm" },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("1")).toHaveAttribute("data-size", "sm");
  },
};
