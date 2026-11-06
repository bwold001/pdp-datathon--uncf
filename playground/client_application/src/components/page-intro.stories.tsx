import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { PageIntro } from "./page-intro";

const meta = {
  component: PageIntro, title: "Components/UI/Page intro",
  args: {
    eyebrow: "Sandbox",
    title: "See the example charts",
    children: <p>Every chart reads the synthetic PDP data through the sandbox API.</p>,
  },
} satisfies Meta<typeof PageIntro>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The title fades in, so it's checked for presence, not visibility. */
export const Default: Story = {
  name: "Page heading at default size",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "See the example charts" })).toBeInTheDocument();
  },
};

export const Small: Story = {
  args: { size: "sm", eyebrow: "No data yet", title: "Start with your AR files" },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Start with your AR files" })).toBeVisible();
  },
};

export const SmallWithoutEyebrow: Story = {
  name: "Small without eyebrow",
  args: { size: "sm", eyebrow: undefined, title: "Your data", children: <p>Last upload today</p> },
  play: async ({ canvas }) => {
    await expect(canvas.queryByText("No data yet")).not.toBeInTheDocument();
  },
};

/** The top-bar label stays visible alongside the page introduction. */
export const InDashboardShell: Story = {
  name: "In dashboard shell",
  args: {
    size: "sm",
    eyebrow: "No data yet",
    title: "Start with your AR files",
    children: <p>Upload your cohort and course files once. Nothing leaves your machine.</p>,
  },
  render: (args) => (
    <DashboardShell shellTitle="Home">
      <div className="p-6">
        <PageIntro {...args} />
      </div>
    </DashboardShell>
  ),
  parameters: { layout: "fullscreen" },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Home")).toBeVisible();
    await expect(canvas.getByRole("heading", { level: 1, name: "Start with your AR files" })).toBeVisible();
  },
};
