import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { describeView, ShareInsightReport } from "./share-insight-report";

const meta = {
  component: ShareInsightReport,
  title: "UNCF/Share Insight report",
  args: { facts: describeView("/uncf/paths", "?pell=Y", 594) },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ShareInsightReport>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The top of a shared PDF: who's counted in words, not the cohort bar's dropdowns. Student paths starts at first-time. */
export const WithFilters: Story = {
  name: "With filters",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Cohort 2023-24 · 594 students")).toBeVisible();
    await expect(canvas.getByText(/Enrollment type: First-time · Pell \(year 1\): Pell recipient/)).toBeVisible();
    await expect(canvas.getByText("Synthetic sample data")).toBeVisible();
    await expect(canvas.queryByRole("combobox")).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button")).not.toBeInTheDocument();
  },
};

/** No filters set: the whole cohort. A tab whose numbers are hidden says so instead of a count. */
export const NoFilters: Story = {
  name: "No filters",
  args: { facts: describeView("/uncf/dfw", "?cohort=2022-23", "under 10") },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Cohort 2022-23 · Fewer than 10 students")).toBeVisible();
    await expect(canvas.getByText(/No filters/)).toBeVisible();
  },
};
