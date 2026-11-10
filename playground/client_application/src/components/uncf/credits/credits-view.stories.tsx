import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { credits2023, credits2024, creditsFall2023, creditsFederalFall2023, creditsSmallGroup, creditsTooFew } from "./credits-fixtures";
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
  args: { data: creditsFall2023 },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof CreditsView>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The tile with this label, so its number can be checked. */
function tile(canvas: ReturnType<typeof within>, label: string) {
  return canvas.getByText(label).parentElement!;
}

/** 2023-24 Fall starters, from the real synthetic data: the values the credit plan checked by hand. */
export const FallStarters: Story = {
  name: "2023-24 Fall starters",
  play: async ({ canvas }) => {
    await expect(tile(canvas, "Avg. credits attempted · year 1")).toHaveTextContent("17.8");
    await expect(tile(canvas, "Avg. credits earned · year 1")).toHaveTextContent("13.1");
    await expect(tile(canvas, "Credit completion ratio")).toHaveTextContent("69%");

    await expect(canvas.getByText("778 · 51%")).toBeVisible();
    await expect(canvas.getByText("316 · 21%")).toBeVisible();
    await expect(canvas.getByText("140 · 9%")).toBeVisible();

    await expect(canvas.getByRole("img", { name: "Fall 2023: 10.3 attempted, 7.3 earned. Spring 2024: 10.6 attempted, 8.4 earned" })).toBeInTheDocument();

    const table = within(canvas.getByRole("table"));
    // The API's default retention is the PDP flag, and the table names it.
    await expect(table.getByRole("columnheader", { name: "Returned here" })).toBeVisible();
    await expect(table.getByRole("row", { name: /^Under 15 929/ })).toHaveTextContent("41%");
    await expect(table.getByRole("row", { name: /^30 or more 140/ })).toHaveTextContent("94%");
    await expect(canvas.getByText(/47 students with blank credits are left out/)).toBeVisible();
    await expect(canvas.queryByText(/next-fall/i)).not.toBeInTheDocument();
  },
};

/** Retention set to Back next fall: the tiers use fall to fall retention, and the labels say so. */
export const FederalRetention: Story = {
  name: "Back next fall",
  args: { data: creditsFederalFall2023 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Credit tiers and retention (back next fall)" })).toBeVisible();
    const table = within(canvas.getByRole("table"));
    await expect(table.getByRole("columnheader", { name: "Back next fall" })).toBeVisible();
    await expect(table.getByRole("row", { name: /^Under 15 929/ })).toHaveTextContent("29%");
    await expect(table.getByRole("row", { name: /^30 or more 140/ })).toHaveTextContent("74%");
    await expect(canvas.getByText(/took a course here in Fall 2024, the fall after year 1/)).toBeVisible();
  },
};

/** A small group: a milestone 1 to 9 students reached shows "Under 10", never the count or its share. */
export const SmallGroup: Story = {
  name: "Small group",
  args: { data: creditsSmallGroup },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("43 · 65%")).toBeVisible();
    await expect(canvas.getByText("15 · 23%")).toBeVisible();
    await expect(canvas.getByRole("img", { name: "30 credits · on pace to graduate on time: Under 10 students" })).toBeInTheDocument();
    await expect(canvas.queryByText(/^6 · /)).not.toBeInTheDocument();
  },
};

/** Every starting term: the two terms differ by student, so they're named by position. */
export const AllStartingTerms: Story = {
  name: "All starting terms",
  args: { data: credits2023 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("First term")).toBeVisible();
    await expect(canvas.getByText("Second term")).toBeVisible();
  },
};

/** The 2024-25 class: its second year is only partly in the data, and the page says so first. */
export const ProvisionalClass: Story = {
  name: "Second year still arriving",
  args: { data: credits2024 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("note")).toHaveTextContent("The 2024-25 class’s second year is only partly in the data.");
  },
};

/** Fewer than 10 students match: no numbers at all. */
export const TooFewStudents: Story = {
  name: "Fewer than 10 students",
  args: { data: creditsTooFew },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Fewer than 10 students with year-1 credits match these filters.")).toBeVisible();
  },
};
