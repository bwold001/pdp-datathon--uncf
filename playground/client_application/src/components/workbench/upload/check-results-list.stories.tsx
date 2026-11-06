import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { blockingCheckResults, mockCheckResults } from "@/components/testing/upload-fixtures";
import { CheckResultsList } from "./check-results-list";

const meta = {
  component: CheckResultsList, title: "Workbench/Upload/Check results list",
  args: { results: mockCheckResults, onFieldClick: fn(), onSave: fn(), onStartOver: fn() },
} satisfies Meta<typeof CheckResultsList>;
export default meta;
type Story = StoryObj<typeof meta>;

/** Warnings and notes only, so saving is allowed. A field button opens that field's definition. */
export const NothingBlocksSaving: Story = {
  name: "Nothing blocks saving",
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("heading", { level: 2 })).toHaveTextContent("Nothing blocks saving. 4 things to know first.");
    const fieldButton = canvas.getByRole("button", { name: "Pell_Status_First_Year" });
    await expect(fieldButton).toHaveAccessibleDescription("Click a field to see its definition.");
    await userEvent.click(fieldButton);
    await expect(args.onFieldClick).toHaveBeenCalledWith("Pell_Status_First_Year");
    await userEvent.click(canvas.getByRole("button", { name: "Save to database" }));
    await expect(args.onSave).toHaveBeenCalledOnce();
    await userEvent.click(canvas.getByRole("button", { name: "Start over" }));
    await expect(args.onStartOver).toHaveBeenCalledOnce();
  },
};

/** An error blocks saving until the files are fixed; starting over still works. */
export const BlockedByAnError: Story = {
  name: "Saving blocked by an error",
  args: { results: blockingCheckResults },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 2 })).toHaveTextContent("1 problem blocks saving.");
    await expect(canvas.getByText(/Blocks saving:/)).toBeInTheDocument();
    await expect(canvas.getByRole("button", { name: "Save to database" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Start over" })).toBeEnabled();
  },
};

export const Saving: Story = {
  name: "Actions disabled during save",
  args: { saving: true },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Saving…" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Start over" })).toBeDisabled();
  },
};

/** Without onFieldClick, as before the context panel is wired, field buttons and their hint are left out. */
export const WithoutFieldLinks: Story = {
  name: "No field help without a click",
  args: { onFieldClick: undefined },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: "Pell_Status_First_Year" })).toBeNull();
    await expect(canvas.queryByText("Click a field to see its definition.")).toBeNull();
  },
};
