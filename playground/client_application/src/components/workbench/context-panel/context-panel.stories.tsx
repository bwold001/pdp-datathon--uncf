import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";
import { Button } from "@/components/ui/button";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ContextPanel, type ContextPanelProps } from "./context-panel";
import { ContextPanelProvider, useContextPanel } from "./context-panel-provider";
import { afterUpload, beforeUpload, caveats, fields, terms } from "@/components/testing/context-panel-fixtures";

const longColumn = "A_very_long_raw_dictionary_column_identifier_without_spaces";
const exampleFields = [...fields, { ...fields[0], id: longColumn, title: "Long column example" }];

function ExampleOpeners() {
  const { openField, fieldId } = useContextPanel();
  return <>
    <p>Synthetic examples for shared panel interactions.</p>
    <div className="flex flex-wrap gap-2">
      <Button onClick={() => openField("Pell_Status_First_Year")}>Explain Pell column</Button>
      <Button onClick={() => openField("Cohort")}>Explain upload check</Button>
      <Button onClick={() => openField("missing")}>Explain missing field</Button>
      <Button onClick={() => openField(longColumn)}>Explain long column</Button>
    </div>
    <output aria-label="Selected field">{fieldId ?? "None"}</output>
  </>;
}
function ExampleShell(args: ContextPanelProps) {
  return <DashboardShell shellTitle="Workbench" contentProvider={ContextPanelProvider} rightSidebar={<ContextPanel {...args} />}>
    <ExampleOpeners />
  </DashboardShell>;
}

// Shown on the Docs page so readers can tell the shell and panel stories apart.
const contextGuide = [
  "**Ready-made context panel for workbench pages.** It is a Dashboard sidebar (frame) with read-only panels that explain the data and single fields. It has no navigation.",
  "**Use it** as `DashboardShell`'s `rightSidebar`, with `contentProvider={ContextPanelProvider}`. Page content opens a field with `useContextPanel().openField(id)`.",
  "**Outside the workbench,** put your own content in a Dashboard sidebar (frame) instead.",
].join("\n\n");

const meta = {
  component: ContextPanel,
  title: "Workbench/Context (right) panel",
  render: ExampleShell,
  args: { fields: exampleFields.map((field) => ({ ...field, profile: undefined })), introduction: beforeUpload, hasData: false, terms, caveats },
  parameters: { layout: "fullscreen", docs: { description: { component: contextGuide } } },
} satisfies Meta<typeof ContextPanel>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Pre-upload state (default)",
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.queryByRole("heading", { name: "Watch out for" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: /Pell grant/ })).not.toBeInTheDocument();
    const right = canvas.getByRole("button", { name: "Toggle context panel" });
    await userEvent.click(right);
    await userEvent.click(canvas.getByRole("button", { name: "Explain Pell column" }));
    await expect(right).toHaveAttribute("aria-expanded", "true");
    await expect(canvas.getByRole("heading", { name: fields[4].title })).toBeInTheDocument();
    await expect(canvas.queryByRole("heading", { name: "In your data" })).not.toBeInTheDocument();
    await expect(canvas.getByLabelText("Selected field")).toHaveTextContent("Pell_Status_First_Year");
    await userEvent.click(canvas.getByRole("button", { name: "About this data" }));
    await expect(canvas.getByLabelText("Selected field")).toHaveTextContent("None");
    await userEvent.click(canvas.getByRole("button", { name: "Explain missing field" }));
    await expect(canvas.getByRole("heading", { name: "Field unavailable" })).toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "About this data" }));
    await userEvent.click(canvas.getByRole("button", { name: "Explain long column" }));
    await expect(canvas.getByRole("heading", { name: "Long column example" })).toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "About this data" }));
    await userEvent.click(canvas.getByRole("button", { name: "Explain upload check" }));
    await expect(canvas.getByRole("heading", { name: "Cohort" })).toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "About this data" }));
  },
};

/** About view after upload: key terms, plus caveats in a "Watch out for" Alert. Synthetic data. */
export const PostUploadTermList: Story = {
  name: "Post-upload state (term list)",
  args: { fields: exampleFields, introduction: afterUpload, hasData: true },
  play: async ({ canvas }) => {
    const keyTerms = canvas.getByRole("heading", { name: "Key terms" }).parentElement!;
    await expect(within(keyTerms).getAllByRole("listitem")).toHaveLength(terms.length);
    const watchOut = canvas.getByRole("note");
    await expect(within(watchOut).getByRole("heading", { name: "Watch out for" })).toBeInTheDocument();
    await expect(within(watchOut).getByText(caveats[0].label)).toBeInTheDocument();
  },
};

/** Field view after upload, with dictionary codes and no profile. Synthetic data. */
export const PostUploadCodeMeaningList: Story = {
  name: "Post-upload state (code meaning list)",
  args: { fields: exampleFields.map((field) => ({ ...field, profile: undefined })), introduction: afterUpload, hasData: true },
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Explain Pell column" }));
    const values = canvas.getByRole("heading", { name: "What the values mean" }).parentElement!;
    await expect(within(values).getAllByRole("listitem")).toHaveLength(fields[4].values!.length);
    await expect(within(values).getByText("Yes")).toBeInTheDocument();
    await expect(canvas.queryByRole("heading", { name: "In your data" })).not.toBeInTheDocument();
  },
};

/** Field view after upload, with a profile and no dictionary codes. Synthetic data. */
export const PostUploadValueDistribution: Story = {
  name: "Post-upload state (value distribution)",
  args: { fields: exampleFields.map((field) => ({ ...field, values: undefined })), introduction: afterUpload, hasData: true },
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Explain Pell column" }));
    await expect(canvas.getByText(/80% of rows/)).toBeInTheDocument();
    await expect(canvas.getAllByRole("progressbar")).toHaveLength(fields[4].profile!.topValues.length);
    await expect(canvas.queryByRole("heading", { name: "What the values mean" })).not.toBeInTheDocument();
  },
};

export const Mobile: Story = {
  name: "Pre-upload state (mobile)",
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Explain Pell column" }));
    const page = within(canvasElement.ownerDocument.body);
    const sheet = await page.findByRole("dialog");
    await expect(within(sheet).getByRole("heading", { name: fields[4].title })).toBeInTheDocument();
    await userEvent.click(within(sheet).getByRole("button", { name: "About this data" }));
    await expect(within(sheet).getByRole("heading", { name: "About this data" })).toBeInTheDocument();
    await userEvent.keyboard("{Escape}");
    await expect(canvas.getByRole("button", { name: "Toggle context panel" })).toHaveAttribute("aria-expanded", "false");
    await userEvent.click(canvas.getByRole("button", { name: "Explain upload check" }));
    await expect(within(await page.findByRole("dialog")).getByRole("heading", { name: "Cohort" })).toBeInTheDocument();
  },
};
