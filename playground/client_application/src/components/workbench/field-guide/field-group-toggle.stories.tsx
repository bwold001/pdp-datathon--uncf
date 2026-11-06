import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { guideGroups } from "@/components/testing/field-guide-fixtures";
import { FieldGroupToggle } from "@/components/workbench/field-guide/field-group-toggle";
const meta = { component: FieldGroupToggle, title: "Workbench/Field guide/Field group toggle", args: { groups: guideGroups, value: "All", onValueChange: fn() } } satisfies Meta<typeof FieldGroupToggle>;
export default meta;
type Story = StoryObj<typeof meta>;
export const SelectGroup: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Course" }));
    await expect(args.onValueChange).toHaveBeenCalledWith("Course");
  },
};
