import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { ExplorerShell } from "./explorer-shell";

const meta = {
  component: ExplorerShell,
  title: "UNCF/Explorer shell",
  args: { children: <h2 className="text-[34px] font-bold">DFW</h2> },
  parameters: {
    layout: "fullscreen",
    nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw" } },
  },
} satisfies Meta<typeof ExplorerShell>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The header, then the four tabs in one row with the current one marked. */
export const OnTheDfwTab: Story = {
  name: "On the DFW tab",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Student Persistence and Pathway Explorer" })).toBeVisible();
    await expect(canvas.getByText("Sample data · illustrative values")).toBeVisible();
    await expect(canvas.queryByRole("button")).not.toBeInTheDocument();

    const tabs = canvas.getAllByRole("link");
    await expect(tabs.map((tab) => tab.textContent)).toEqual(["Student paths", "DFW", "Gateway courses", "Credit momentum"]);
    await expect(tabs.map((tab) => tab.getAttribute("href"))).toEqual([
      "/uncf/paths",
      "/uncf/dfw",
      "/uncf/gateway",
      "/uncf/credit-momentum",
    ]);
    await expect(canvas.getByRole("link", { name: "DFW" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.getByRole("link", { name: "Student paths" })).not.toHaveAttribute("aria-current");

    // Horizontal: every tab sits on the same line, left to right.
    const boxes = tabs.map((tab) => tab.getBoundingClientRect());
    await expect(new Set(boxes.map((box) => Math.round(box.top))).size).toBe(1);
    await expect(boxes.every((box, i) => i === 0 || box.left > boxes[i - 1].left)).toBe(true);
  },
};

/** The design's light colors hold even when the app is in dark mode. */
export const StaysLightInDarkMode: Story = {
  name: "Stays light in dark mode",
  play: async ({ canvas, canvasElement }) => {
    const root = canvasElement.ownerDocument.documentElement;
    root.classList.add("dark");
    try {
      const shell = canvas.getByRole("main").parentElement!;
      await expect(getComputedStyle(shell).backgroundColor).toBe("rgb(244, 244, 242)");
      await expect(getComputedStyle(canvas.getByRole("banner")).backgroundColor).toBe("rgb(255, 255, 255)");
    } finally {
      root.classList.remove("dark");
    }
  },
};

/** The tab content renders under the tabs. */
export const RendersTheTab: Story = {
  name: "Renders the tab's page",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/credit-momentum" } } },
  args: { children: <h2>Credit Momentum</h2> },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("main")).toContainElement(canvas.getByRole("heading", { level: 2, name: "Credit Momentum" }));
    await expect(canvas.getByRole("link", { name: "Credit momentum" })).toHaveAttribute("aria-current", "page");
  },
};
