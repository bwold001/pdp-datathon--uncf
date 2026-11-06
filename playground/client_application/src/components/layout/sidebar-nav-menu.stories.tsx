import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { HouseIcon, TableIcon } from "lucide-react";
import { expect, fn } from "storybook/test";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { SidebarNavMenu } from "./sidebar-nav-menu";

// Shown on the Docs page so readers can tell the four sidebar stories apart.
const navMenuGuide = [
  "**Building block: a list of nav links, with no frame.** It marks `activeHref` as the current page and calls `onNavigate` on a plain click.",
  "**Use it** inside a Dashboard sidebar (frame) to make a left navigation. Your page decides which link is active and what happens on navigate, such as closing the mobile sheet.",
  "**In the workbench,** use Workbench/Navigation (left) panel instead. It already wraps this menu with the workbench links.",
].join("\n\n");

const meta = {
  component: SidebarNavMenu, title: "Components/Layout/Sidebar building blocks/Sidebar nav menu (links)",
  args: { items: [{ label: "Home", href: "#home", icon: HouseIcon }, { label: "Explore data", href: "#explore", icon: TableIcon }], activeHref: "#home", onNavigate: fn() },
  render: (args) => <DashboardShell shellTitle="Navigation example" leftSidebar={<DashboardSidebar><SidebarNavMenu {...args} /></DashboardSidebar>}><p>Navigation takes props, with no database dependency.</p></DashboardShell>,
  parameters: { layout: "fullscreen", docs: { description: { component: navMenuGuide } } },
} satisfies Meta<typeof SidebarNavMenu>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = {
  name: "Default: Check navigation semantics",
  play: async ({ canvas, args, userEvent }) => {
    await expect(canvas.getByRole("navigation", { name: "Main navigation" })).toBeInTheDocument();
    await expect(canvas.getByRole("link", { name: "Home" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.getByRole("link", { name: "Explore data" })).not.toHaveAttribute("aria-current");
    await userEvent.click(canvas.getByRole("link", { name: "Explore data" }));
    await expect(args.onNavigate).toHaveBeenCalledOnce();
  },
};
