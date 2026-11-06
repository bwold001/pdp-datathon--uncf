import { useState, type ComponentProps } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { FieldSearch } from "@/components/workbench/field-guide/field-search";

/** Supplies the controlled query value for the search example. */
function SearchExample(args: ComponentProps<typeof FieldSearch>) {
  const [value, setValue] = useState(args.value);
  return (
    <FieldSearch value={value} onValueChange={(next) => { setValue(next); args.onValueChange(next); }} />
  );
}
const meta = { component: FieldSearch, title: "Workbench/Field guide/Field search", args: { value: "", onValueChange: fn() }, render: (args) => <SearchExample {...args} /> } satisfies Meta<typeof FieldSearch>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Search: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Search fields" }), "Pell");
    await expect(args.onValueChange).toHaveBeenLastCalledWith("Pell");
  },
};
