import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, spyOn, waitFor } from "storybook/test";

import { ExplorerShell } from "./explorer-shell";
import { ViewIntro } from "./view-intro";

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

/** The header, then the five tabs in one row with the current one marked. */
export const OnTheDfwTab: Story = {
  name: "On the DFW tab",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Student Persistence and Pathway Explorer" })).toBeVisible();
    await expect(canvas.getByText("Synthetic sample data")).toBeVisible();
    await expect(canvas.getByText("Synthetic sample data. Nothing here describes real students or institutions.")).toBeVisible();
    await expect(canvas.queryByRole("button", { name: /Export/ })).not.toBeInTheDocument();
    await expect(canvas.getByRole("region", { name: "Who's shown" })).toBeVisible();

    const tabs = canvas.getAllByRole("link");
    await expect(tabs.map((tab) => tab.textContent)).toEqual(["Student paths", "DFW", "Gateway courses", "Credit momentum", "Chat"]);
    await expect(tabs.map((tab) => tab.getAttribute("href"))).toEqual([
      "/uncf/paths",
      "/uncf/dfw",
      "/uncf/gateway",
      "/uncf/credit-momentum",
      "/uncf/chat",
    ]);
    await expect(canvas.getByRole("link", { name: "DFW" })).toHaveAttribute("aria-current", "page");
    await expect(canvas.getByRole("link", { name: "Student paths" })).not.toHaveAttribute("aria-current");

    // Horizontal: every tab sits on the same line, left to right.
    const boxes = tabs.map((tab) => tab.getBoundingClientRect());
    await expect(new Set(boxes.map((box) => Math.round(box.top))).size).toBe(1);
    await expect(boxes.every((box, i) => i === 0 || box.left > boxes[i - 1].left)).toBe(true);
  },
};

/** The cohort filters travel with the tab links, but a tab's own query values (a sort order) don't. */
export const KeepsFiltersAcrossTabs: Story = {
  name: "Keeps filters across tabs",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/paths", query: { pell: "Y", sort: "rate" } } } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("link", { name: "DFW" })).toHaveAttribute("href", "/uncf/dfw?pell=Y");
    await expect(canvas.getByRole("button", { name: "Remove Pell recipient" })).toBeVisible();
  },
};

/** Only filters someone set travel: Student paths' own first-time start stays on that tab. */
export const CarriesOnlyFiltersSomeoneSet: Story = {
  name: "Carries only filters someone set",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/gateway", query: { retention_type: "federal" } } } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("link", { name: "Student paths" })).toHaveAttribute("href", "/uncf/paths?retention_type=federal");
    await expect(canvas.getByRole("link", { name: "Credit momentum" })).toHaveAttribute(
      "href",
      "/uncf/credit-momentum?retention_type=federal",
    );
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

/** Share Insight, beside the tab's title, draws the tab and hands the browser a PDF to download. */
export const SharesTheTabAsAPdf: Story = {
  name: "Shares the tab as a PDF",
  args: {
    children: (
      <ViewIntro title="DFW" whatThisShows="Grades of D, F or W." howToRead="Longer bars, more students." keyTerms="DFW rate.">
        Where students struggle.
      </ViewIntro>
    ),
  },
  play: async ({ canvas, userEvent }) => {
    const button = canvas.getByRole("button", { name: "Share Insight" });
    await expect(canvas.getByRole("main")).toContainElement(button);
    await expect(canvas.getByRole("banner")).not.toContainElement(button);

    const createObjectURL = spyOn(URL, "createObjectURL");
    try {
      await userEvent.click(button);
      await waitFor(() => expect(createObjectURL).toHaveBeenCalled(), { timeout: 15000 });
      await expect((createObjectURL.mock.calls[0][0] as Blob).type).toBe("application/pdf");
      await expect(canvas.getByRole("button", { name: "Share Insight" })).toBeEnabled();
    } finally {
      createObjectURL.mockRestore();
    }
  },
};
