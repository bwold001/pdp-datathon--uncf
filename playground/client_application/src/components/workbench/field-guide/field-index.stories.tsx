import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { guideSections } from "@/components/testing/field-guide-fixtures";
import { FieldIndex } from "@/components/workbench/field-guide/field-index";
const meta = { component: FieldIndex, title: "Workbench/Field guide/Field index", args: { sections: guideSections, selectedId: "cohort.pell", onSelect: fn() } } satisfies Meta<typeof FieldIndex>;
export default meta;
type Story = StoryObj<typeof meta>;
export const GroupedFields: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("button", { name: "Pell grant" })).toHaveAttribute("aria-current", "true");
    await userEvent.click(canvas.getByRole("button", { name: /FAFSA application/ }));
    await expect(args.onSelect).toHaveBeenCalledWith("aid.fafsa");
    await expect(canvas.getByText("not in data")).toBeVisible();
  },
};
export const NoMatchingFields: Story = {
  args: { sections: [] },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("No fields match")).toBeVisible();
  },
};
