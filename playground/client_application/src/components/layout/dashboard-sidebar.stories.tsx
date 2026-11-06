import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { DashboardSidebar } from "./dashboard-sidebar";

// Shown on the Docs page so readers can tell the four sidebar stories apart.
const sidebarGuide = [
  "**Building block: the empty frame inside a sidebar.** It lays out an optional header, one content group and an optional footer. It has no content of its own.",
  "**Use it** to build a new sidebar for either side of `DashboardShell`. Pass your content as children; for links, use Sidebar nav menu.",
  "**In the workbench,** don't build on it directly. Use Workbench/Navigation (left) panel or Workbench/Context (right) panel, which are both built on this frame.",
].join("\n\n");

const meta = {
  component: DashboardSidebar, title: "Components/Layout/Sidebar building blocks/Dashboard sidebar (frame)",
  args: { title: "AR Workbench", shortTitle: "AR", label: "Workbench", footer: <p className="px-2 text-sm">Footer slot</p>, children: <p className="px-2 text-sm">Content slot</p> },
  render: (args) => (
    <DashboardShell shellTitle="Sidebar example" leftSidebar={<DashboardSidebar {...args} />} rightSidebar={<DashboardSidebar><p className="px-2 text-sm">Panel content only</p></DashboardSidebar>}>
      <p>Both sidebars use the same base.</p>
    </DashboardShell>
  ),
  parameters: { layout: "fullscreen", docs: { description: { component: sidebarGuide } } },
} satisfies Meta<typeof DashboardSidebar>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Header, content and footer",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("AR Workbench")).toBeVisible();
    await expect(canvas.getByText("Workbench", { exact: true })).toBeVisible();
    await expect(canvas.getByText("Content slot")).toBeVisible();
    await expect(canvas.getByText("Footer slot")).toBeVisible();
    await expect(canvas.getByText("Panel content only")).toBeVisible();
  },
};

/** The short title replaces the title in the icon rail. */
export const Collapsed: Story = {
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Toggle navigation" }));
    await expect(canvas.getByText("AR Workbench")).not.toBeVisible();
    await expect(canvas.getByText("AR", { exact: true })).toBeVisible();
  },
};
