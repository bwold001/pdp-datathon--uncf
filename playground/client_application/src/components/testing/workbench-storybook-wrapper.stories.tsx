import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { Button } from "@/components/ui/button";
import { useContextPanel } from "@/components/workbench/context-panel/context-panel-provider";
import { afterUpload, beforeUpload } from "./context-panel-fixtures";
import { WorkbenchStorybookWrapper } from "./workbench-storybook-wrapper";

/** Stands in for a real page; it opens a field to show page content reaches the context panel. */
function PlaceholderPageWithField() {
  const { openField } = useContextPanel();
  return <>
    <h1 className="text-2xl font-semibold">Placeholder page</h1>
    <Button className="self-start" onClick={() => openField("Pell_Status_First_Year")}>Explain Pell column</Button>
  </>;
}

// Shown on the Docs page so readers know this is a story helper, not a component to ship.
const wrapperGuide = [
  "**Story helper for workbench pages.** It puts a page inside `DashboardShell` with the navigation panel, the context panel and their synthetic fixtures.",
  "**Use it** in a page's stories: pass `page` for the current link, `hasData` for before or after an upload, and `showContextPanel={false}` for the field guide.",
].join("\n\n");

const meta = {
  component: WorkbenchStorybookWrapper,
  title: "Testing/Workbench Storybook wrapper",
  args: { page: "home", hasData: false, children: <PlaceholderPageWithField /> },
  parameters: { layout: "fullscreen", docs: { description: { component: wrapperGuide } } },
} satisfies Meta<typeof WorkbenchStorybookWrapper>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Home before data is loaded",
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByRole("link", { name: "Home" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.getByText("no data", { exact: true })).toBeVisible();
    await expect(canvas.getByText(beforeUpload)).toBeInTheDocument();
    await expect(canvas.queryByRole("heading", { name: "Watch out for" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Explain Pell column" }));
    await expect(canvas.getByRole("heading", { name: "Did they get a Pell grant in year 1?" })).toBeInTheDocument();
    await expect(canvas.queryByRole("heading", { name: "In your data" })).not.toBeInTheDocument();
  },
};

/** After an upload: the database lists its tables and the context panel shows the caveats. */
export const DataLoaded: Story = {
  name: "Explore with data loaded",
  args: { page: "explore", hasData: true },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("link", { name: "Explore data" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.queryByText("no data", { exact: true })).not.toBeInTheDocument();
    await expect(canvas.getByRole("status")).toHaveTextContent("2 tables · cohort, course");
    await expect(canvas.getByText(afterUpload)).toBeInTheDocument();
    await expect(canvas.getByRole("heading", { name: "Watch out for" })).toBeInTheDocument();
  },
};

/** The field guide explains fields itself, so it has no context panel or its toggle. */
export const WithoutContextPanel: Story = {
  name: "Field guide without the context panel",
  args: { page: "fields", showContextPanel: false, children: <h1 className="text-2xl font-semibold">Placeholder page</h1> },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("link", { name: "Field guide" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.queryByRole("button", { name: "Toggle context panel" })).not.toBeInTheDocument();
    await expect(canvas.getByRole("heading", { level: 1, name: "Placeholder page" })).toBeInTheDocument();
  },
};
