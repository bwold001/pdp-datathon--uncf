import { useState, type ComponentProps } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, waitFor, within } from "storybook/test";
import { FilterChipMenu } from "@/components/workbench/explore/filter-chip-menu";

/** Models URL-owned selection without controlling the menu or its search box. */
function FilterExample(args: ComponentProps<typeof FilterChipMenu>) {
  const [selectedValues, setSelectedValues] = useState(args.selectedValues);
  return (
    <FilterChipMenu {...args} selectedValues={selectedValues} onSelectionChange={(values) => {
      setSelectedValues(values);
      args.onSelectionChange(values);
    }} />
  );
}
const meta = {
  component: FilterChipMenu,
  title: "Workbench/Explore/Filter chip menu",
  args: {
    label: "Pell", question: "Did they receive a Pell grant?", selectedValues: [],
    options: [{ value: "yes", label: "Yes", count: 10313 }, { value: "no", label: "No", count: 25 }],
    onSelectionChange: fn(), onExplain: fn(), onOpenChange: fn(),
  },
  render: (args) => <FilterExample {...args} />,
} satisfies Meta<typeof FilterChipMenu>;
export default meta;
type Story = StoryObj<typeof meta>;

export const LocalMenuAndSearch: Story = {
  play: async ({ args, canvas, canvasElement, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Pell: Any" }));
    const page = within(canvasElement.ownerDocument.body);
    // The popover fades in from opacity 0, so wait for it to finish opening.
    await waitFor(() => expect(page.getByText("10,313")).toBeVisible());
    await userEvent.type(page.getByRole("textbox", { name: "Search Pell options" }), "no match");
    await expect(page.getByText("No options match")).toBeVisible();
    await userEvent.clear(page.getByRole("textbox", { name: "Search Pell options" }));
    await userEvent.click(page.getByRole("checkbox", { name: /Yes/ }));
    await expect(args.onSelectionChange).toHaveBeenCalledWith(["yes"]);
    await expect(canvas.getByRole("button", { name: "Pell: Yes" })).toBeVisible();
    await userEvent.click(page.getByRole("button", { name: "Clear" }));
    await expect(args.onSelectionChange).toHaveBeenLastCalledWith([]);
  },
};
export const Explain: Story = {
  play: async ({ args, canvas, canvasElement, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Pell: Any" }));
    await userEvent.click(within(canvasElement.ownerDocument.body).getByRole("button", { name: "What is this?" }));
    await expect(args.onExplain).toHaveBeenCalledOnce();
    await expect(args.onOpenChange).toHaveBeenLastCalledWith(false);
  },
};
export const ControlledOpen: Story = {
  args: { open: true, searchable: false },
  play: async ({ canvasElement }) => {
    const page = within(canvasElement.ownerDocument.body);
    await waitFor(async () => {
      await expect(page.getByRole("checkbox", { name: /Yes/ })).toBeVisible();
    });
    await expect(page.queryByRole("textbox")).not.toBeInTheDocument();
  },
};
