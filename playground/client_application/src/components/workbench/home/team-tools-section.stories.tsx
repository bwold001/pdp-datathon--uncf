import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { homeTools } from "@/components/testing/home-fixtures";
import { TeamToolsSection } from "@/components/workbench/home/team-tools-section";

const meta = {
  component: TeamToolsSection,
  title: "Workbench/Home/Team tools section",
  args: homeTools,
} satisfies Meta<typeof TeamToolsSection>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Tools: Story = {
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Team tools" })).toBeVisible();
    await expect(canvas.getAllByRole("link")).toHaveLength(2);
    await expect(canvas.getByRole("link", { name: /Add your tool/ })).toHaveAttribute("href", "#add");
  },
};
