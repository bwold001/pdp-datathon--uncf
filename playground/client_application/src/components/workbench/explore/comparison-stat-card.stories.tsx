import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { ComparisonStatCard } from "@/components/workbench/explore/comparison-stat-card";

const meta = { component: ComparisonStatCard, title: "Workbench/Explore/Comparison stat card" } satisfies Meta<typeof ComparisonStatCard>;
export default meta;
type Story = StoryObj<typeof ComparisonStatCard>;
export const Count: Story = {
  args: { kind: "count", label: "Students", value: 10313, total: 12000 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("10,313")).toBeVisible();
    await expect(canvas.getByText("of 12,000 students")).toBeVisible();
  },
};
export const Rate: Story = { args: { kind: "rate", label: "Retained", value: 62, baseline: 57 } };
export const NoBaseline: Story = {
  args: { kind: "rate", label: "Retained", value: 62, baseline: null },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("All students: no reported values")).toBeVisible();
  },
};
export const NoReportedValues: Story = {
  args: { kind: "rate", label: "Retained", value: null, baseline: 57 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("No reported values in this group")).toBeVisible();
    await expect(canvas.getByText("—")).toBeVisible();
  },
};
