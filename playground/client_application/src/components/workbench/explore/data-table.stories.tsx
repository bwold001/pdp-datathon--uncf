import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { exploreRows, type ExploreRow } from "@/components/testing/explore-fixtures";
import { DataTable, type DataTableColumn } from "@/components/workbench/explore/data-table";

const columns: DataTableColumn<ExploreRow>[] = [
  { accessorKey: "id", header: "Student ID" },
  { accessorKey: "Cohort", header: "Starting cohort" },
];
const meta = {
  component: DataTable<ExploreRow>,
  title: "Workbench/Explore/Data table",
  args: { columns, data: exploreRows.slice(0, 3), caption: "Synthetic student examples", onHeaderClick: fn(), onRetry: fn() },
} satisfies Meta<typeof DataTable<ExploreRow>>;
export default meta;
type Story = StoryObj<typeof meta>;

export const RowsAndFieldHelp: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByText("S0001")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Starting cohort" }));
    await expect(args.onHeaderClick).toHaveBeenCalledWith("Cohort");
  },
};
export const HiddenColumn: Story = {
  args: { columnVisibility: { Cohort: false } },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: "Starting cohort" })).not.toBeInTheDocument();
    await expect(canvas.getByText("S0001")).toBeVisible();
  },
};
export const Loading: Story = {
  args: { loading: true },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("Loading rows");
    await expect(canvas.queryByText("S0001")).not.toBeInTheDocument();
  },
};
export const ErrorWithRetry: Story = {
  args: { error: "The students could not be loaded." },
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("alert")).toHaveTextContent("could not be loaded");
    await userEvent.click(canvas.getByRole("button", { name: "Try again" }));
    await expect(args.onRetry).toHaveBeenCalledOnce();
  },
};
export const NoMatchingStudents: Story = {
  args: { data: [] },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("No students match")).toBeVisible();
  },
};
