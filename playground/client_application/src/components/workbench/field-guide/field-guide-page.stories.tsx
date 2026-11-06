import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, within } from "storybook/test";
import { guideFields, guideGroups, guideSections } from "@/components/testing/field-guide-fixtures";
import { WorkbenchStorybookWrapper } from "@/components/testing/workbench-storybook-wrapper";
import { FieldGuidePage, type FieldGuidePageProps } from "@/components/workbench/field-guide/field-guide-page";

/** Demonstrates caller-owned search, grouping and selection using synthetic definitions. */
function GuideExample(args: FieldGuidePageProps) {
  const [query, setQuery] = useState(args.search.value);
  const [group, setGroup] = useState(args.groups.value);
  const [selectedId, setSelectedId] = useState(args.detail.field?.id);
  const matching = guideFields.filter((field) => (group === "All" || field.group === group)
    && `${field.title} ${field.id} ${field.description}`.toLowerCase().includes(query.toLowerCase()));
  const selected = matching.find((field) => field.id === selectedId) ?? matching[0];
  const sections = guideSections.map((section) => ({ ...section, fields: section.fields.filter((field) => matching.some((match) => match.id === field.id)) }));
  return (
    <FieldGuidePage
      {...args}
      search={{ value: query, onValueChange: (next) => { setQuery(next); args.search.onValueChange(next); } }}
      groups={{ ...args.groups, value: group, onValueChange: (next) => { setGroup(next); args.groups.onValueChange(next); } }}
      index={{ sections, selectedId: selected?.id, onSelect: (next) => { setSelectedId(next); args.index.onSelect(next); } }}
      detail={{ ...args.detail, field: selected }}
    />
  );
}
const meta = {
  component: FieldGuidePage,
  title: "Workbench/Field guide/Field guide page",
  args: {
    search: { value: "", onValueChange: fn() },
    groups: { groups: guideGroups, value: "All", onValueChange: fn() },
    index: { sections: guideSections, selectedId: "cohort.pell", onSelect: fn() },
    detail: { field: guideFields[0], profileSource: "mock" },
  },
  render: (args) => <GuideExample {...args} />,
  decorators: [(Story) => (
    <WorkbenchStorybookWrapper page="fields" hasData showContextPanel={false}>
      <Story />
    </WorkbenchStorybookWrapper>
  )],
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof FieldGuidePage>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Field guide" })).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Toggle context panel" })).not.toBeInTheDocument();
  },
};
export const SearchAndSelect: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.type(canvas.getByRole("textbox", { name: "Search fields" }), "FAFSA");
    await userEvent.click(canvas.getByRole("button", { name: /FAFSA application/ }));
    await expect(args.index.onSelect).toHaveBeenCalledWith("aid.fafsa");
    await expect(canvas.getByRole("heading", { name: "FAFSA application" })).toBeVisible();
  },
};
export const FieldNotInData: Story = {
  args: { detail: { field: guideFields[2], profileSource: "uploaded" } },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Not in this data")).toBeVisible();
    await expect(canvas.queryByRole("heading", { name: "In your data" })).not.toBeInTheDocument();
  },
};
export const NoMatchingFields: Story = {
  args: { search: { ...meta.args.search, value: "nothing matches this query" } },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("No fields match")).toBeVisible();
    await expect(canvas.getByRole("heading", { name: "Choose a field" })).toBeVisible();
  },
};
export const FilterGroup: Story = {
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Course" }));
    const index = within(canvas.getByRole("navigation", { name: "Field index" }));
    await expect(index.getAllByRole("button")).toHaveLength(1);
    await expect(canvas.getByRole("heading", { name: "Gateway math" })).toBeVisible();
  },
};
export const Mobile: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Field guide" })).toBeVisible();
    const document = canvasElement.ownerDocument.documentElement;
    await expect(document.scrollWidth).toBeLessThanOrEqual(document.clientWidth);
  },
};
