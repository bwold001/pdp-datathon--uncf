import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { UploadStatusLine } from "@/components/workbench/home/upload-status-line";

const meta = {
  component: UploadStatusLine,
  title: "Workbench/Home/Upload status line",
  args: { lastUpload: "today", warningCount: 0 },
} satisfies Meta<typeof UploadStatusLine>;
export default meta;
type Story = StoryObj<typeof UploadStatusLine>;

export const PassedChecks: Story = {
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Last upload today · all files passed checks")).toBeVisible();
  },
};
export const OneWarning: Story = {
  args: { warningCount: 1 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/1 warning from the checks/)).toBeVisible();
  },
};
export const Warnings: Story = {
  args: { warningCount: 1234 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/1,234 warnings from the checks/)).toBeVisible();
  },
};
export const UnavailableChecks: Story = {
  args: { warningCount: null },
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/check results unavailable/)).toBeVisible();
    await expect(canvas.queryByText(/all files passed/)).not.toBeInTheDocument();
  },
};
