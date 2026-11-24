import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { gateway2023, gateway2024, gatewayFederal2023, gatewayPell2023, gatewayTooFew } from "./gateway-fixtures";
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
    const eng = canvas.getByRole("button", { name: /^ENG 101/ });
    await expect(eng).toHaveAttribute("aria-pressed", "true");
    await expect(eng).toHaveTextContent("384");
    await expect(eng).toHaveTextContent("73%");
    await expect(canvas.getByText("passed on the first try: 281 of 384 students")).toBeVisible();
    await expect(canvas.getByRole("img", { name: /Passed on the first try: 281, Retook it and passed: 18, Retook it, still didn’t pass: 9, Didn’t pass, didn’t retake: 76/ })).toBeVisible();
    await expect(canvas.getByRole("img", { name: "C or higher: 249, Below C: 17, Under 1.0: 65, P: 50, W: 31" })).toBeVisible();
    await userEvent.click(canvas.getByText("How grades are counted"));
    await expect(canvas.getByRole("row", { name: /^Below C 1\.0 to under 2\.0/ })).toHaveTextContent("No, didn’t pass");
    await expect(canvas.getAllByRole("listitem")).toHaveLength(10);
    await userEvent.click(canvas.getByRole("button", { name: "Show 10 more of 109" }));
    await expect(canvas.getAllByRole("listitem")).toHaveLength(20);
    await userEvent.selectOptions(canvas.getByRole("combobox", { name: /Sort by/ }), "first");
    await expect(canvas.getAllByRole("listitem")[0]).toHaveTextContent("0%");
    await expect(canvas.getByText(/pairs have 1 or more students/)).toBeVisible();
  },
};

/** Fall to fall retention: the page names the measure the Retention filter picked. */
export const BackNextFall: Story = {
  name: "Back next fall",
  args: { data: gatewayFederal2023 },
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/Back next fall, these students:/)).toHaveTextContent("42%");

    await expect(canvas.getByText(/took a course here in Fall 2024, the fall after year 1/)).toBeVisible();
  },
};

/** Pell recipients: each course compares them with everyone else who took it. */
export const PellRecipients: Story = {
  name: "Pell recipients vs. everyone else",
  args: { data: gatewayPell2023, groupLabel: "Pell (year 1): Pell recipient" },
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByText("Comparing Pell (year 1): Pell recipient with everyone else who took each course.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: /^ENG 101/ })).toBeVisible();
    await userEvent.selectOptions(canvas.getByRole("combobox", { name: /Sort by/ }), "gap");
    await expect(canvas.getAllByRole("listitem").length).toBeGreaterThan(0);
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
export const SmallGroupVisible: Story = {
  name: "Two students stay visible",
  args: { data: gatewayTooFew },
  play: async ({ canvas }) => {
    await expect(canvas.getByText("passed on the first try: 1 of 1 students")).toBeVisible();
    await expect(canvas.queryByText(/hidden to protect privacy/)).not.toBeInTheDocument();
  },
};
