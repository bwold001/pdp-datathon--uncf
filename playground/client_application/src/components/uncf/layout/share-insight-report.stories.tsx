import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { describeView, ShareInsightReport } from "./share-insight-report";

const meta = {
  component: ShareInsightReport,
  title: "UNCF/Share Insight report",
  args: { facts: describeView("/uncf/paths", "?pell=Y", 594, "synthetic") },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ShareInsightReport>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The top of a shared PDF: who's counted in words, not the cohort bar's dropdowns. Student paths starts at first-time. */
export const WithFilters: Story = {
  name: "With filters",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Cohort 2023-24 · 594 students")).toBeVisible();
    await expect(canvas.getByText("Enrollment type:").parentElement).toHaveTextContent("Enrollment type: First-time");
    await expect(canvas.getByText("Pell (year 1):").parentElement).toHaveTextContent("Pell (year 1): Pell recipient");
    await expect(canvas.getByText("Synthetic sample data")).toBeVisible();
    await expect(canvas.queryByRole("combobox")).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button")).not.toBeInTheDocument();
  },
};

/** Gateway and Credit momentum list the retention measure, which changes their numbers, even at its default. */
export const WithRetention: Story = {
  name: "With the retention measure",
  args: { facts: describeView("/uncf/gateway", "?retention_type=federal&gender=F", 530, "synthetic") },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Retention:").parentElement).toHaveTextContent("Retention: Back next fall");
    await expect(canvas.getByText("Gender:").parentElement).toHaveTextContent("Gender: Female");
    await expect(canvas.queryByText(/^Cohort:/)).not.toBeInTheDocument();
  },
};

/** No filters set: the whole cohort. A tab with too few students to show says so instead of a count. */
export const NoFilters: Story = {
  name: "No filters",
  args: { facts: describeView("/uncf/dfw", "?cohort=2022-23", "too few", "synthetic") },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Cohort 2022-23 · Too few students to show")).toBeVisible();
    await expect(canvas.getByText("None. Every student in the cohort.")).toBeVisible();
  },
};

/** On a school's own PDP files, the report says so and never calls the numbers synthetic. */
export const OnInstitutionData: Story = {
  name: "On the institution's data",
  args: { facts: describeView("/uncf/paths", "", 594, "institution") },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Institution PDP data")).toBeVisible();
    await expect(canvas.queryByText(/synthetic/i)).not.toBeInTheDocument();
  },
};
