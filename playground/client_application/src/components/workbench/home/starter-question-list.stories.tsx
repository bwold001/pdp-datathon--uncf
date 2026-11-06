import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { homeData } from "@/components/testing/home-fixtures";
import { StarterQuestionList } from "@/components/workbench/home/starter-question-list";

const meta = {
  component: StarterQuestionList,
  title: "Workbench/Home/Starter question list",
  args: homeData.questions,
} satisfies Meta<typeof StarterQuestionList>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Questions: Story = {
  play: async ({ canvas, userEvent }) => {
    const link = canvas.getByRole("link", { name: /How many students receive Pell grants/ });
    await expect(link).toHaveAttribute("href", "#pell");
    await userEvent.click(link);
  },
};
