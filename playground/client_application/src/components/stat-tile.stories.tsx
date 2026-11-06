import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { StatTile, StatTileSkeleton } from "./stat-tile";

const meta = {
  component: StatTile, title: "Components/UI/Stat tile",
  args: { value: "10,313", label: "students in the cohort file" },
} satisfies Meta<typeof StatTile>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Value and label",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("10,313")).toBeVisible();
    await expect(canvas.getByText("students in the cohort file")).toBeVisible();
  },
};

export const WithUnitAndDetail: Story = {
  name: "With unit and detail",
  args: { value: "62", unit: "%", label: "came back for year 2", detail: "2023-24 starting cohort" },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("%")).toBeVisible();
    await expect(canvas.getByText("2023-24 starting cohort")).toBeVisible();
  },
};

export const Loading: Story = { render: () => <StatTileSkeleton /> };
