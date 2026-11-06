import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { FilteredStudentsSummary } from "@/components/workbench/explore/filtered-students-summary";
const meta = { component: FilteredStudentsSummary, title: "Workbench/Explore/Filtered students summary", args: { children: "24 synthetic students match these filters." } } satisfies Meta<typeof FilteredStudentsSummary>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Summary: Story = {
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("24 synthetic students");
  },
};
