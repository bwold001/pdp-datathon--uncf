import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, within } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import {
  credits2024,
  creditsFall2022,
  creditsFall2022Pell,
  creditsFederalFall2023,
  creditsSmallGroup,
  creditsTooFew,
} from "./credits-fixtures";
import { CreditsView } from "./credits-view";

const meta = {
  component: CreditsView,
  title: "UNCF/Credit momentum/Page",
  decorators: [
    (Story) => (
      <ExplorerStoryFrame>
        <Story />
      </ExplorerStoryFrame>
    ),
  ],
  args: { data: creditsFall2022 },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof CreditsView>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The card for one of the two questions, by its heading. */
function question(canvas: ReturnType<typeof within>, heading: RegExp) {
  return canvas.getByRole("heading", { name: heading }).closest("section")!;
}

/** Fall 2022 starters, the class in the design: every number traces to the API's progress answer (synthetic data). */
export const DesignClass: Story = {
  name: "Fall 2022 starters",
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Credit momentum · year 1 · class that started Fall 2022")).toBeVisible();
    await expect(canvas.getByText("4-year pace:").parentElement).toHaveTextContent("4-year pace: 120 credits ÷ 4 years = 30 a year");

    const minimum = within(question(canvas, /^1 · Did they do the minimum\?/));
    await expect(minimum.getByText("19%")).toBeVisible();
    await expect(minimum.getByText("did. About 1 in 5.")).toBeVisible();
    await expect(minimum.getByText(/^305 of 1,589 students earned 24 or more credits/)).toBeVisible();
    await expect(minimum.getByText(/did the minimum in year 1 and again in year 2/)).toHaveTextContent("8% did the minimum in year 1 and again in year 2 (123 students).");

    const pace = within(question(canvas, /^2 · Are they on pace to finish in 4 years\?/));
    await expect(pace.getByText("8%")).toBeVisible();
    await expect(pace.getByText("are. About 1 in 12.")).toBeVisible();
    await expect(pace.getByText(/if the school sets 125 credits/)).toHaveTextContent("5% if the school sets 125 credits (more than 31 a year).");
    await expect(pace.getByText(/still on pace after 2 years/)).toHaveTextContent("4% are still on pace after 2 years (60 or more credits).");

    const table = within(canvas.getByRole("table"));
    await expect(table.getByRole("columnheader", { name: "Returned here" })).toBeVisible();
    await expect(table.getByRole("row", { name: /^On 4-year pace/ })).toHaveTextContent("30 or more133 · 8%95%");
    await expect(table.getByRole("row", { name: /^Did the minimum, slower/ })).toHaveTextContent("24 to 29172 · 11%90%");
    await expect(table.getByRole("row", { name: /^Below the minimum/ })).toHaveTextContent("Under 24763 · 48%68%");
    await expect(table.getByRole("row", { name: /^Stopped after the first term/ })).toHaveTextContent("Under 24, no courses in Spring 2023521 · 33%25%");

    await expect(canvas.getByRole("heading", { name: "Why 763 fell below the minimum" })).toBeVisible();
    await expect(canvas.getByRole("img", { name: "Signed up for fewer than 24: 539 · 71%" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Signed up for enough, failed: 110 · 14%" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Signed up for enough, withdrew: 66 · 9%" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Passed enough, not all of it counts: 31 · 4%" })).toBeInTheDocument();
    await expect(canvas.getByText(/^17 more had incomplete or missing grades/)).toBeVisible();

    await expect(canvas.getByRole("img", { name: "Did the minimum again: 123 · 40%" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Kept taking courses, fell under 24: 99 · 32%" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Took no courses in year 2: 83 · 27%" })).toBeInTheDocument();
    await expect(canvas.getByText("Only 123 of 1,589 students (8%) did the minimum in both years.")).toBeVisible();
    await expect(canvas.getByRole("link", { name: "Where they went: Student paths" })).toHaveAttribute("href", "/uncf/paths");
  },
};

/** With filters set, the page says who it covers, and Clear filters clears the cohort bar's added filters. */
export const Filtered: Story = {
  args: { data: creditsFall2022Pell, filters: { text: "Fall · Pell recipient", onClear: fn() }, linkQuery: "cohort=2022-23&cohort_term=Fall&pell=Y" },
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByText(/Every number below covers only these students/)).toHaveTextContent(
      "Showing 623 students: Fall · Pell recipient. Every number below covers only these students.",
    );
    await userEvent.click(canvas.getByRole("button", { name: "Clear filters" }));
    await expect(args.filters!.onClear).toHaveBeenCalled();
    // Links to other tabs keep the same students.
    await expect(canvas.getAllByRole("link", { name: "Which courses: DFW tab" })[0]).toHaveAttribute("href", "/uncf/dfw?cohort=2022-23&cohort_term=Fall&pell=Y");
  },
};

/** Retention set to Back next fall: the groups' retention column names it. */
export const FederalRetention: Story = {
  name: "Back next fall",
  args: { data: creditsFederalFall2023 },
  play: async ({ canvas }) => {
    await expect(within(canvas.getByRole("table")).getByRole("columnheader", { name: "Back next fall" })).toBeVisible();
    await expect(canvas.getByText(/took a course here in Fall 2024, the fall after year 1/)).toBeVisible();
  },
};

/** The 2024-25 class: its second year is only partly in the data, so the page says year 2 will change. */
export const ProvisionalClass: Story = {
  name: "Second year still arriving",
  args: { data: credits2024 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("note")).toHaveTextContent("The 2024-25 class’s second year is only partly in the data.");
    // Start terms differ, so the class is named by its year and "stopped" by the next fall or spring term.
    await expect(canvas.getByText("Credit momentum · year 1 · class that entered in 2024-25")).toBeVisible();
    await expect(within(canvas.getByRole("table")).getByRole("row", { name: /^Stopped/ })).toHaveTextContent("Under 24, no courses in the next fall or spring term");
  },
};

/** A small group: groups and reasons of 1 to 9 students show "Under 10", never a count or share. */
export const SmallGroup: Story = {
  name: "Small group",
  args: { data: creditsSmallGroup },
  play: async ({ canvas }) => {
    const table = within(canvas.getByRole("table"));
    await expect(table.getByRole("row", { name: /^On 4-year pace/ })).toHaveTextContent("Under 10–");
    await expect(table.getByRole("row", { name: /^Below the minimum/ })).toHaveTextContent("32 · 48%81%");
    await expect(canvas.getByRole("img", { name: "Signed up for enough, failed: Under 10" })).toBeInTheDocument();
    // On pace is under 10, so its big share is hidden too.
    await expect(question(canvas, /^2 · /)).toHaveTextContent(/^2 · Are they on pace to finish in 4 years\?–/);
  },
};

/** Fewer than 10 students match: the heading, then no numbers at all. */
export const TooFewStudents: Story = {
  name: "Fewer than 10 students",
  args: { data: creditsTooFew },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Are students making meaningful progress toward their degree?" })).toBeVisible();
    await expect(canvas.getByText("Fewer than 10 students match these filters.")).toBeVisible();
  },
};
