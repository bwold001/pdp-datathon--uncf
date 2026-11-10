import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { gateway2023, gateway2024, gatewayPell2023, gatewayTooFew } from "./gateway-fixtures";
import { GatewayView } from "./gateway-view";

const meta = {
  component: GatewayView,
  title: "UNCF/Gateway courses/Page",
  decorators: [
    (Story) => (
      <ExplorerStoryFrame>
        <Story />
      </ExplorerStoryFrame>
    ),
  ],
  args: { data: gateway2023 },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof GatewayView>;
export default meta;
type Story = StoryObj<typeof meta>;

/** 2023-24 from the real synthetic data: the course list, ENG 101's path, and the course pairs. */
export const RealCourses: Story = {
  name: "2023-24 gateway courses",
  play: async ({ canvas, userEvent }) => {
    // The institution flags its gateway courses, so there's no "not flagged" notice.
    await expect(canvas.queryByRole("note")).not.toBeInTheDocument();

    // Biggest course first, and selected: 297 of 384 passed on the first try, 313 in the end.
    const eng = canvas.getByRole("button", { name: /^ENG 101/ });
    await expect(eng).toHaveAttribute("aria-pressed", "true");
    await expect(eng).toHaveTextContent("384");
    await expect(eng).toHaveTextContent("77%");
    await expect(eng).toHaveTextContent("82%");
    await expect(canvas.getByText("passed on the first try: 297 of 384 students")).toBeVisible();
    await expect(canvas.getByRole("img", { name: /Passed on the first try: 297, Retook it and passed: 16, Retook it, still didn’t pass: hidden, Didn’t pass, didn’t retake: 64/ })).toBeVisible();

    // With no filter, there's no group to compare.
    await expect(canvas.getByText("Pick a group in the filters above to compare it with everyone else in each course.")).toBeVisible();
    await expect(canvas.getByRole("option", { name: "Group furthest behind" })).toBeDisabled();

    // Ten rows, then ten more of 27.
    const list = canvas.getAllByRole("listitem");
    await expect(list).toHaveLength(10);
    await userEvent.click(canvas.getByRole("button", { name: "Show 10 more of 27" }));
    await expect(canvas.getAllByRole("listitem")).toHaveLength(20);

    // Sorting by the lowest first-try pass puts MAT 162 on top.
    await userEvent.selectOptions(canvas.getByRole("combobox", { name: /Sort by/ }), "first");
    await expect(canvas.getAllByRole("listitem")[0]).toHaveTextContent("MAT 162");

    // Pairs are compared with everyone else, and say when a gap could be chance.
    await expect(canvas.getByText(/Retention for these students:/)).toHaveTextContent("52%");
    await expect(canvas.getByText("6 of 13 students who took both in their first term came back · could be chance")).toBeVisible();
    await expect(canvas.getByText(/^35 pairs have 10 or more students/)).toBeVisible();
  },
};

/** Pell recipients: each course compares them with everyone else who took it. */
export const PellRecipients: Story = {
  name: "Pell recipients vs. everyone else",
  args: { data: gatewayPell2023, groupLabel: "Pell (year 1): Pell recipient" },
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByText("Comparing Pell (year 1): Pell recipient with everyone else who took each course.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: /^ENG 101/ })).toHaveTextContent("−6.2");
    await expect(canvas.getByText("−6.2 pts")).toBeVisible();
    await expect(canvas.getByText(/passes on the first try less often than everyone else\. Could be chance\./)).toBeVisible();

    // Furthest behind first: ENG 121 at −17.7 points.
    await userEvent.selectOptions(canvas.getByRole("combobox", { name: /Sort by/ }), "gap");
    await expect(canvas.getAllByRole("listitem")[0]).toHaveTextContent("ENG 121");
    await expect(within(canvas.getAllByRole("listitem")[0]).getByText("−17.7")).toBeVisible();
  },
};

/** The 2024-25 class: its next year is only partly in the data, and the page says so first. */
export const ProvisionalClass: Story = {
  name: "Next year still arriving",
  args: { data: gateway2024 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("note")).toHaveTextContent("The next year is only partly in the data.");
  },
};

/** Fewer than 10 students match: no numbers at all. */
export const TooFewStudents: Story = {
  name: "Fewer than 10 students",
  args: { data: gatewayTooFew },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Fewer than 10 students match these filters.")).toBeVisible();
  },
};
