import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { guideFields } from "@/components/testing/field-guide-fixtures";
import { FieldGuideArticle } from "@/components/workbench/field-guide/field-guide-article";

const meta = { component: FieldGuideArticle, title: "Workbench/Field guide/Field guide article", args: { field: guideFields[0], filterAction: { onClick: fn() } } } satisfies Meta<typeof FieldGuideArticle>;
export default meta;
type Story = StoryObj<typeof meta>;
export const DefinitionAndMockProfile: Story = {
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("heading", { name: "In the mock data" })).toBeVisible();
    await expect(canvasElement.querySelector("strong")).toHaveTextContent("Federal aid");
    await expect(canvas.getByText("Yes")).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Filter the data by this field" })).not.toBeInTheDocument();
  },
};
export const BeforeUpload: Story = {
  args: { field: { ...guideFields[0], profile: undefined } },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("heading", { name: "In the mock data" })).not.toBeInTheDocument();
  },
};
export const UploadedProfile: Story = {
  args: { profileSource: "uploaded" },
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("heading", { name: "In your data" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Filter the data by this field" }));
    await expect(args.filterAction?.onClick).toHaveBeenCalledOnce();
  },
};
export const NotInData: Story = {
  args: { field: { ...guideFields[2], profile: guideFields[0].profile }, profileSource: "uploaded" },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Not in this data")).toBeVisible();
    await expect(canvas.queryByRole("heading", { name: "In your data" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: "Filter the data by this field" })).not.toBeInTheDocument();
  },
};
export const NoSelection: Story = { args: { field: undefined } };
