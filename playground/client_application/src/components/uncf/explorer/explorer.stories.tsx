import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, waitFor } from "storybook/test";

import { Explorer } from "./explorer";
import { loadPathsSample, loadSample } from "./explorer-samples";

const meta = {
  component: Explorer,
  title: "UNCF/Explorer/Explorer",
  args: { load: loadSample, loadYearTwo: loadPathsSample },
} satisfies Meta<typeof Explorer>;
export default meta;
type Story = StoryObj<typeof Explorer>;

export const Default: Story = {
  play: async ({ canvas }) => {
    await expect(await canvas.findByRole("heading", { name: /Returned here by Pell grant · entered 2022–23/ })).toBeVisible();
    // The definition sits beside the chart.
    await expect(canvas.getByRole("heading", { name: "Returned here", level: 2 })).toBeVisible();
    await expect(canvas.getByText("PDP name: Retention")).toBeVisible();
    // The comparison names both groups and works the gap out from the shown rates.
    await expect(canvas.getByText(/Pell grant 58\.9%, No Pell grant 53\.7% \(5\.2 points apart\)/)).toBeVisible();
    // Each bar has a trend across entering classes, read out as text.
    await expect(canvas.getAllByText(/^Trend across entering classes:/).length).toBeGreaterThan(0);
    // The year-2 paths chart is labeled as mock data.
    await expect(await canvas.findByText("Mock data")).toBeVisible();
    // The card link carries the view.
    await expect(canvas.getByRole("link", { name: /Create insight card/ })).toHaveAttribute(
      "href",
      "/uncf/card?cohort=2022-23&group_by=pell&measure=retention",
    );
  },
};

export const SwitchToGatewayMath: Story = {
  play: async ({ canvas }) => {
    await canvas.findByRole("heading", { name: /Returned here by Pell grant/ });
    await userEvent.click(canvas.getByRole("button", { name: "Gateway math" }));
    await expect(await canvas.findByRole("heading", { name: /Gateway math by Pell grant/ })).toBeVisible();
    await expect(canvas.getByText(/Read gateway rates with care/)).toBeVisible();
    await expect(canvas.getByText(/518 students with an unknown requirement or result are left out/)).toBeVisible();
  },
};

export const AddASecondGrouping: Story = {
  play: async ({ canvas }) => {
    await canvas.findByRole("heading", { name: /Returned here by Pell grant/ });
    await userEvent.click(canvas.getByRole("button", { name: "Add a second grouping" }));
    await expect(
      await canvas.findByRole("heading", { name: /Returned here by Pell grant and full- or part-time status/ }),
    ).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Remove the second grouping" }));
    await waitFor(() => expect(canvas.queryByRole("button", { name: "Remove the second grouping" })).toBeNull());
  },
};

export const NotSavedShowsAnError: Story = {
  play: async ({ canvas }) => {
    await canvas.findByRole("heading", { name: /Returned here by Pell grant/ });
    await userEvent.selectOptions(canvas.getByRole("combobox", { name: "Group students by" }), "race");
    await expect(await canvas.findByText("These results couldn't load.")).toBeVisible();
    await expect(canvas.getByText("This combination isn't saved yet.")).toBeVisible();
    await expect(canvas.getAllByRole("button", { name: /Try again/ }).length).toBeGreaterThan(0);
  },
};
