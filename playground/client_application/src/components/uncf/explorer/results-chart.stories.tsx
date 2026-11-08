import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { buildBars } from "./bars";
import { gatewayMathByPell, notYetAndNotReported, retentionByGender, retentionByPell, retentionByPellAndLoad } from "./explorer-samples";
import { ResultsChart } from "./results-chart";

/** The chart's props for one sample response. */
function argsFor(response: typeof retentionByPell, mode: "plain" | "analyst" = "plain") {
  const { everyone, sections } = buildBars(response);
  return { measure: response.meta.measure, everyone, sections, mode };
}

const meta = { component: ResultsChart, title: "UNCF/Explorer/Results chart" } satisfies Meta<typeof ResultsChart>;
export default meta;
type Story = StoryObj<typeof ResultsChart>;

export const ByPell: Story = {
  args: argsFor(retentionByPell),
  play: async ({ canvas }) => {
    // Rates are worked out from the counts and shown to one decimal.
    await expect(canvas.getByText("58.9%")).toBeVisible();
    await expect(canvas.getByText("873 students")).toBeVisible();
    await expect(canvas.getByText("54.0%")).toBeVisible();
  },
};

export const AnalystCounts: Story = {
  args: argsFor(retentionByPell, "analyst"),
  play: async ({ canvas }) => {
    await expect(canvas.getByText("514 of 873")).toBeVisible();
  },
};

export const HiddenGroupIsNeverZero: Story = {
  args: argsFor(retentionByGender),
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Gender X")).toBeVisible();
    await expect(canvas.getByText("Hidden")).toBeVisible();
    await expect(canvas.getByText("Hidden to protect privacy. This does not mean 0.")).toBeInTheDocument();
    await expect(canvas.queryByText("0.0%")).toBeNull();
  },
};

export const GatewayRequiredCounts: Story = {
  args: argsFor(gatewayMathByPell),
  play: async ({ canvas }) => {
    await expect(canvas.getByText("448 required")).toBeVisible();
  },
};

export const TwoGroupings: Story = {
  args: argsFor(retentionByPellAndLoad),
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Pell grant" })).toBeVisible();
    await expect(canvas.getByRole("heading", { name: "No Pell grant" })).toBeVisible();
    // A hidden combination is listed by name, not drawn as an empty bar.
    await expect(canvas.getByText(/fewer than 10 students, so it is hidden/)).toBeVisible();
    await expect(canvas.getByText("Small group")).toBeVisible();
  },
};

export const NotAvailableYetAndNotReported: Story = {
  args: argsFor(notYetAndNotReported),
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText("Not reported").length).toBeGreaterThan(0);
    await expect(canvas.getByText("Not available yet")).toBeVisible();
    await expect(canvas.queryByText("0.0%")).toBeNull();
  },
};
