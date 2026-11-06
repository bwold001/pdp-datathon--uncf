import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, within } from "storybook/test";
import { exploreRows, type ExploreRow } from "@/components/testing/explore-fixtures";
import { WorkbenchStorybookWrapper } from "@/components/testing/workbench-storybook-wrapper";
import type { DataTableColumn } from "@/components/workbench/explore/data-table";
import { ExplorePage, type ExplorePageProps } from "@/components/workbench/explore/explore-page";

/** Supplies a controlled snapshot so the example's filters and language toggle work. */
function ExploreExample(args: ExplorePageProps<ExploreRow>) {
  const [mode, setMode] = useState(args.mode.value);
  const [filters, setFilters] = useState(args.filters);
  const columns: DataTableColumn<ExploreRow>[] = [
    { accessorKey: "id", header: mode === "plain" ? "Student ID" : "Student_GUID" },
    { accessorKey: "Cohort", header: mode === "plain" ? "Starting cohort" : "Cohort" },
    { accessorKey: "Pell_Status_First_Year", header: mode === "plain" ? "Pell grant" : "Pell_Status_First_Year" },
  ];
  const rows = args.table.data.filter((row) => filters.every((filter) =>
    filter.selectedValues.length === 0 || filter.selectedValues.includes(String(row[filter.id as keyof ExploreRow])),
  ));
  return (
    <ExplorePage
      {...args}
      mode={{ value: mode, onChange: (next) => { setMode(next); args.mode.onChange(next); } }}
      filters={filters.map((filter) => ({ ...filter, onSelectionChange: (values) => {
        setFilters((current) => current.map((item) => item.id === filter.id ? { ...item, selectedValues: values } : item));
        filter.onSelectionChange(values);
      } }))}
      filterBar={{ onClearAll: () => {
        setFilters((current) => current.map((filter) => ({ ...filter, selectedValues: [] })));
        args.filterBar.onClearAll();
      } }}
      summary={{ children: `${rows.length.toLocaleString("en-US")} synthetic example rows shown.` }}
      table={{ ...args.table, columns, data: rows }}
    />
  );
}
const meta = {
  component: ExplorePage<ExploreRow>,
  title: "Workbench/Explore/Explore page",
  args: {
    mode: { value: "plain", onChange: fn() },
    filters: [{ id: "Pell_Status_First_Year", label: "Pell", question: "Did they receive a Pell grant?", options: [{ value: "Yes", label: "Yes", count: 32 }, { value: "No", label: "No", count: 16 }], selectedValues: [], onSelectionChange: fn(), onExplain: fn() }],
    filterBar: { onClearAll: fn() },
    stats: [
      { id: "count", kind: "count", label: "Matching students", value: 48, total: 48 },
      { id: "rate", kind: "rate", label: "Retained", value: 75, baseline: 75 },
    ],
    summary: { children: "Synthetic example students" },
    table: { columns: [], data: exploreRows.slice(0, 25), caption: "Synthetic students, not real findings", onHeaderClick: fn(), pagination: { pageIndex: 0, pageSize: 25, totalRows: 48, onPrevious: fn(), onNext: fn() } },
  },
  render: (args) => <ExploreExample {...args} />,
  decorators: [(Story) => (
    <WorkbenchStorybookWrapper page="explore" hasData>
      <Story />
    </WorkbenchStorybookWrapper>
  )],
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ExplorePage<ExploreRow>>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Clear all" })).toBeDisabled();
    await expect(canvas.getByText("S0001")).toBeVisible();
  },
};
export const FiltersDeriveClearState: Story = {
  play: async ({ canvas, canvasElement, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Pell: Any" }));
    const page = within(canvasElement.ownerDocument.body);
    await userEvent.click(page.getByRole("checkbox", { name: /Yes/ }));
    await userEvent.keyboard("{Escape}");
    await expect(canvas.getByRole("button", { name: "Clear all" })).toBeEnabled();
    await userEvent.click(canvas.getByRole("button", { name: "Clear all" }));
    await expect(canvas.getByRole("button", { name: "Clear all" })).toBeDisabled();
  },
};
export const AnalystMode: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Analyst" }));
    await expect(args.mode.onChange).toHaveBeenCalledWith("analyst");
    await expect(canvas.getByRole("button", { name: "Pell_Status_First_Year" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Plain language" }));
    await expect(canvas.getByRole("button", { name: "Pell grant" })).toBeVisible();
  },
};
export const NoMatchingStudents: Story = {
  args: { table: { ...meta.args.table, data: [], pagination: { ...meta.args.table.pagination, totalRows: 0 } } },
  play: async ({ canvas }) => {
    await expect(within(canvas.getByRole("table")).getByText("No students match")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  },
};
export const LastPage: Story = {
  args: { table: { ...meta.args.table, data: exploreRows.slice(25), pagination: { ...meta.args.table.pagination, pageIndex: 1 } } },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("26–48 of 48 students")).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
  },
};
export const Mobile: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("heading", { name: "Explore data", level: 1 })).toBeVisible();
    const document = canvasElement.ownerDocument.documentElement;
    await expect(document.scrollWidth).toBeLessThanOrEqual(document.clientWidth);
  },
};
