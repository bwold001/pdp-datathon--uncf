import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, waitFor, within } from "storybook/test";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { sidebarDestinations } from "@/components/testing/navigation-panel-fixtures";
import { NavigationPanel } from "./navigation-panel";

// Shown on the Docs page so readers can tell the shell and panel stories apart.
const navigationGuide = [
  "**Ready-made navigation panel for workbench pages.** It is a Dashboard sidebar (frame) holding a Sidebar nav menu (links) with the four workbench pages, plus the local database status in the footer.",
  "**Use it** as `DashboardShell`'s `leftSidebar` on every workbench page. Pass `currentPath` and it picks the active link, including nested routes.",
  "**Outside the workbench,** build your own from the two Sidebar building blocks instead.",
].join("\n\n");

const meta = {
  component: NavigationPanel, title: "Workbench/Navigation (left) panel",
  args: { destinations: sidebarDestinations, currentPath: sidebarDestinations.home, database: { status: "empty" } },
  render: (args) => <DashboardShell shellTitle="Workbench" leftSidebar={<NavigationPanel {...args} />}><p>Synthetic Workbench navigation panel examples.</p></DashboardShell>,
  parameters: { layout: "fullscreen", docs: { description: { component: navigationGuide } } },
} satisfies Meta<typeof NavigationPanel>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: before data is loaded",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("navigation", { name: "Workbench" })).toBeInTheDocument();
    await expect(canvas.getByRole("link", { name: "Back to playground" })).toHaveAttribute("href", "#playground");
    await expect(canvas.getAllByRole("link")).toHaveLength(5);
    await expect(canvas.getByRole("link", { name: "Home" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.getByText("no data", { exact: true })).toBeVisible();
    await expect(canvas.getByRole("status")).toHaveTextContent("Empty · no files yet");
  },
};
export const DatabaseLoaded: Story = {
  name: "Database loaded",
  args: { database: { status: "loaded", tables: ["cohort", "course"] }, currentPath: sidebarDestinations.explore },
  play: async ({ canvas }) => {
    await expect(canvas.queryByText("no data", { exact: true })).not.toBeInTheDocument();
    await expect(canvas.getByRole("status")).toHaveTextContent("2 tables · cohort, course");
    await expect(canvas.getByRole("link", { name: "Explore data" })).toHaveAttribute("aria-current", "page");
  },
};
/** Loading and unavailable never show the "no data" note: only a confirmed empty database does. */
export const DatabaseLoading: Story = {
  name: "Database loading",
  args: { database: { status: "loading" } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("Checking local database…");
    await expect(canvas.queryByText("no data", { exact: true })).not.toBeInTheDocument();
  },
};
export const DatabaseUnavailable: Story = {
  name: "Database unavailable",
  args: { database: { status: "unavailable" } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("Unavailable · could not connect");
    await expect(canvas.queryByText("no data", { exact: true })).not.toBeInTheDocument();
  },
};
export const NestedRoute: Story = {
  name: "Nested route",
  args: { destinations: { home: "/workbench", upload: "/workbench/upload", explore: "/workbench/explore", fields: "/workbench/fields" }, currentPath: "/workbench/fields/Cohort" },
  play: async ({ canvas }) => { await expect(canvas.getByRole("link", { name: "Field guide" })).toHaveAttribute("aria-current", "page"); },
};
export const Collapsed: Story = {
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Toggle navigation" }));
    await expect(canvas.getByRole("button", { name: "Toggle navigation" })).toHaveAttribute("aria-expanded", "false");
    await expect(canvas.getByRole("link", { name: "Home" })).toBeVisible();
    await expect(canvas.getByRole("status")).toHaveAccessibleName("Local database: Empty · no files yet");
  },
};
export const Mobile: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Toggle navigation" }));
    const page = within(canvasElement.ownerDocument.body);
    const sheet = await page.findByRole("dialog");
    await expect(within(sheet).getByRole("status")).toHaveTextContent("Empty · no files yet");
    await userEvent.click(within(sheet).getByRole("link", { name: "Upload files" }));
    await waitFor(() => expect(page.queryByRole("dialog")).not.toBeInTheDocument());
    await expect(canvas.getByRole("button", { name: "Toggle navigation" })).toHaveAttribute("aria-expanded", "false");
  },
};
