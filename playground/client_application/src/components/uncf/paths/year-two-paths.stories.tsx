import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent } from "storybook/test";

import { loadPathsSample } from "@/components/uncf/explorer/explorer-samples";

import { YearTwoPaths } from "./year-two-paths";

const meta = {
  component: YearTwoPaths,
  title: "UNCF/Explorer/Year-2 paths (mock)",
  args: { cohort: "2022-23", groupBy: ["pell"], mode: "plain", load: loadPathsSample },
} satisfies Meta<typeof YearTwoPaths>;
export default meta;
type Story = StoryObj<typeof YearTwoPaths>;

export const ByPell: Story = {
  play: async ({ canvas }) => {
    await expect(await canvas.findByText("Mock data")).toBeVisible();
    // Shares are of everyone who entered: 343 of 2,617 moved.
    await expect(canvas.getAllByText("13.1%").length).toBeGreaterThan(0);
    await expect(canvas.getByRole("img", { name: /343 moved to another college/ })).toBeInTheDocument();
    await expect(canvas.getByRole("heading", { name: "Year-2 paths for each group" })).toBeVisible();
  },
};

export const PickAGroup: Story = {
  play: async ({ canvas }) => {
    await canvas.findByText("Mock data");
    await userEvent.click(canvas.getByRole("button", { name: /^No Pell grant/ }));
    await expect(canvas.getByRole("img", { name: /No Pell grant who entered/ })).toBeInTheDocument();
  },
};

export const AsATable: Story = {
  play: async ({ canvas }) => {
    await canvas.findByText("Mock data");
    await userEvent.click(canvas.getByRole("button", { name: "Show as table" }));
    await expect(canvas.getByRole("table")).toBeVisible();
    await expect(canvas.getByRole("cell", { name: "Moved: 4-year college" })).toBeVisible();
  },
};

export const HiddenGroupIsNeverZero: Story = {
  args: { groupBy: ["gender"] },
  play: async ({ canvas }) => {
    await canvas.findByText("Mock data");
    await userEvent.selectOptions(canvas.getByRole("combobox"), "X");
    await expect(canvas.getByText("Hidden to protect privacy")).toBeVisible();
    await expect(canvas.getByText(/Gender X has fewer than 10 students/)).toBeVisible();
  },
};
