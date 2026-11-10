import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { allStarters2023, everyEnrollmentType2023, fallStarters2023, fallStarters2024, tooFewStudents } from "./paths-fixtures";
import { PathsView } from "./paths-view";

const meta = {
  component: PathsView,
  title: "UNCF/Student paths/Page",
  decorators: [
    (Story) => (
      <ExplorerStoryFrame>
        <Story />
      </ExplorerStoryFrame>
    ),
  ],
  args: { data: fallStarters2023 },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PathsView>;
export default meta;
type Story = StoryObj<typeof meta>;

/** The tile with this label, so its number and note can be checked. */
function tile(canvas: ReturnType<typeof within>, label: string) {
  return canvas.getByText(label).parentElement!;
}

/** 2023-24 Fall starters, from the real synthetic data: every number traces to the API's answer. */
export const FallStarters: Story = {
  name: "2023-24 Fall starters",
  play: async ({ canvas, canvasElement }) => {
    await expect(tile(canvas, "Entering cohort")).toHaveTextContent("1,114");
    await expect(tile(canvas, "Entering cohort")).toHaveTextContent("First-time, Fall 2023");
    await expect(tile(canvas, "Still here · Fall 2024")).toHaveTextContent("47%");
    await expect(tile(canvas, "Enrolled anywhere · Fall 2024")).toHaveTextContent("52%");
    // Those tiles count one term, so they don't borrow the PDP names, which mean the year-2 flags.
    await expect(canvas.queryByText(/^Retention|^Persistence/)).not.toBeInTheDocument();
    await expect(tile(canvas, "Stopped out by Fall 2024")).toHaveTextContent("45%96 students returned after a term away");

    await expect(canvas.getByRole("img", { name: /^Flow of 1,114 students \(First-time\)/ })).toBeInTheDocument();
    const bandTitles = [...canvasElement.querySelectorAll("path > title")].map((title) => title.textContent);
    await expect(bandTitles).toContain("Returned after a term away · 96");
    await expect(bandTitles).toContain("Stayed enrolled to Fall 2024 · 423");
    // Earned a credential here: the API's fourth status, so the year-2 column adds up to everyone who entered.
    await expect(bandTitles).toContain("Enrolled in Spring 2024, earned a credential by Fall 2024 · 13");
    await expect(bandTitles).toContain("No record in Spring 2024, earned a credential by Fall 2024 · 13");
    await expect(canvas.getByText("27 · 2%")).toBeInTheDocument();
    // Moves of 1 to 9 students are hidden, so they get no band.
    await expect(bandTitles.some((title) => title?.startsWith("Came back from another college"))).toBe(false);

    await expect(canvas.getByText("Of 60 students who transferred out by Fall 2024")).toBeVisible();
    await expect(canvas.getByRole("img", { name: "To a 4-year institution: 35" })).toBeInTheDocument();
    await expect(canvas.getByRole("img", { name: "Other, mixed or not recorded: Under 10" })).toBeInTheDocument();

    const table = within(canvas.getByRole("table"));
    await expect(table.getByRole("row", { name: "Fall 2023 1,114 – – –" })).toBeVisible();
    await expect(table.getByRole("row", { name: "Spring 2024 642 0 33 439" })).toBeVisible();
    await expect(table.getByRole("row", { name: "Fall 2024 522 27 60 505" })).toBeVisible();
  },
};

/** Enrollment type set to All: every Fall starter, and the tiles say so instead of "First-time". */
export const EveryEnrollmentType: Story = {
  name: "Every enrollment type",
  args: { data: everyEnrollmentType2023 },
  play: async ({ canvas }) => {
    await expect(tile(canvas, "Entering cohort")).toHaveTextContent("1,584");
    await expect(tile(canvas, "Entering cohort")).toHaveTextContent("All enrollment types, Fall 2023");
    await expect(canvas.getByRole("img", { name: /^Flow of 1,584 students \(All enrollment types\)/ })).toBeInTheDocument();
    await expect(canvas.queryByText(/First-time/)).not.toBeInTheDocument();
  },
};

/** Every starting term at once: the terms differ by student, so they're named by their place in the path. */
export const AllStartingTerms: Story = {
  name: "All starting terms",
  args: { data: allStarters2023 },
  play: async ({ canvas }) => {
    await expect(tile(canvas, "Entering cohort")).toHaveTextContent("First-time, 2023-24");
    await expect(canvas.getByText("Still here · year 2")).toBeVisible();
    await expect(canvas.getByText("Entered")).toBeInTheDocument();
    await expect(canvas.getByRole("row", { name: /^Entering term/ })).toBeVisible();
    await expect(canvas.getByRole("row", { name: /^The next term/ })).toBeVisible();
  },
};

/** The 2024-25 class: its second year is only partly in the data, and the page says so first. */
export const ProvisionalClass: Story = {
  name: "Class with year 2 still arriving",
  args: { data: fallStarters2024 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("note")).toHaveTextContent("The 2024-25 class’s second year is still arriving.");
  },
};

/** Fewer than 10 students match: no numbers at all, and a way forward. */
export const TooFewStudents: Story = {
  name: "Fewer than 10 students",
  args: { data: tooFewStudents },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Fewer than 10 students match these filters.")).toBeVisible();
    await expect(canvas.queryByRole("table")).not.toBeInTheDocument();
  },
};
