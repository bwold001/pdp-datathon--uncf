import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, spyOn, within } from "storybook/test";

import { ExplorerProvider } from "@/components/uncf/layout/explorer-context";
import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { dfwList2023, eng101Detail2023 } from "./dfw-fixtures";
import { DfwPage } from "./dfw-page";

/** Answers the page's two requests with the saved real answers, as the API would. */
function answerFromFixtures() {
  const spy = spyOn(window, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    const body = url.includes("/uncf/dfw/course") ? eng101Detail2023 : dfwList2023;
    return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
  });
  return () => spy.mockRestore();
}

const meta = {
  component: DfwPage,
  title: "UNCF/DFW/Page",
  decorators: [
    (Story) => (
      <ExplorerProvider>
        <ExplorerStoryFrame>
          <Story />
        </ExplorerStoryFrame>
      </ExplorerProvider>
    ),
  ],
  beforeEach: answerFromFixtures,
  parameters: { layout: "fullscreen", nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw" } } },
} satisfies Meta<typeof DfwPage>;
export default meta;
type Story = StoryObj<typeof meta>;

/** 2023-24 from the real synthetic data: tiles, the ranked list, and ENG 101 (the top course) in detail. */
export const RealCourses: Story = {
  name: "2023-24 courses",
  play: async ({ canvas, userEvent }) => {
    await expect(await canvas.findByText("4,347 of 18,883 final grades were a D, F or W")).toBeVisible();
    await expect(canvas.getByText("23.0%")).toBeVisible();
    await expect(canvas.getByText("2,870 final grades below a C")).toBeVisible();
    await expect(canvas.getByText("1,477 withdrawals")).toBeVisible();

    const list = within(canvas.getByRole("list"));
    const rows = list.getAllByRole("button");
    await expect(rows).toHaveLength(10);
    await expect(rows[0]).toHaveTextContent("ENG 101");
    await expect(rows[0]).toHaveAttribute("aria-pressed", "true");

    // The detail card: ENG 101, and Pell recipients 4.2 points above everyone else in the course.
    await expect(await canvas.findByRole("heading", { name: "ENG 101" })).toBeVisible();
    await expect(canvas.getByText("135 of 492 final grades were a D, F or W")).toBeVisible();
    await expect(canvas.getByText("Listed in the catalog as COMPOSITION I · ENG-101 · ENGLISH COMP 1 and 8 more")).toBeVisible();
    await expect(canvas.getByText("+4.2 pts")).toBeVisible();

    await userEvent.click(canvas.getByRole("button", { name: "Show 10 more" }));
    await expect(within(canvas.getByRole("list")).getAllByRole("button").length).toBeGreaterThan(10);

    await userEvent.click(canvas.getByRole("button", { name: "DFW rate" }));
    await expect(canvas.getByText(/Small courses can top this list/)).toBeVisible();
    const byRate = within(canvas.getByRole("list")).getAllByRole("button");
    await expect(byRate.length).toBe(10);
    await expect(byRate[0]).not.toHaveTextContent("ENG 101");
  },
};

/** Comparing by race in ENG 101: groups under 10 students are named, not shown. */
export const HiddenGroups: Story = {
  name: "Groups under 10 are hidden",
  play: async ({ canvas, userEvent }) => {
    await canvas.findByRole("heading", { name: "ENG 101" });
    await userEvent.click(canvas.getByRole("button", { name: "Race" }));
    await expect(
      canvas.getByText(
        "Hidden to protect privacy (under 10 students): American Indian or Alaska Native, Native Hawaiian or Other Pacific Islander",
      ),
    ).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Delivery" }));
    await expect(canvas.getByText(/^Online/)).toBeVisible();
  },
};

/** The size cutoff: only courses with at least 100 final grades. */
export const SizeCutoff: Story = {
  name: "Size cutoff",
  play: async ({ canvas, userEvent }) => {
    await canvas.findByRole("heading", { name: "ENG 101" });
    await userEvent.selectOptions(canvas.getByRole("combobox"), "100");
    const rows = within(canvas.getByRole("list")).getAllByRole("button");
    const grades = rows.map((row) => Number(row.querySelector(".uncf-num.hidden, .uncf-num.sm\\:block")?.textContent?.replace(/,/g, "")));
    await expect(grades.every((count) => count >= 100)).toBe(true);
    await expect(canvas.getByText(/with at least 100 final grades$/)).toBeVisible();
  },
};
