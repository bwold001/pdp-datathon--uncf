import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { ExplorerStoryFrame } from "@/components/uncf/layout/explorer-story-frame";

import { gateway2023, gateway2024, gatewayFall2023, gatewayFederal2023, gatewayTooFew } from "./gateway-fixtures";
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

/** 2023-24 from the real synthetic data, with the API's default retention (the PDP flag): the outcomes and the pairs. */
export const RealCourses: Story = {
  name: "2023-24 gateway courses",
  play: async ({ canvas, userEvent }) => {
    // The institution flags its gateway courses, so there's no "inferred" notice.
    await expect(canvas.queryByRole("note")).not.toBeInTheDocument();

    const table = within(canvas.getByRole("table"));
    const eng = table.getByRole("row", { name: /^ENG 101/ });
    await expect(eng).toHaveTextContent("380");
    await expect(within(eng).getByRole("img")).toHaveAccessibleName("73% passed (a–c), 20% d or f, 7% withdrew");
    await expect(eng).toHaveTextContent("79%");
    await expect(eng).toHaveTextContent("38%");
    // The columns name the measure the numbers use, not a fixed "next fall".
    await expect(table.getByRole("columnheader", { name: "Returned here if passed" })).toBeVisible();
    await expect(canvas.queryByText(/next-fall/i)).not.toBeInTheDocument();

    // Both subjects show before "Show all": five English and five math courses.
    const rows = table.getAllByRole("row").slice(1);
    await expect(rows.filter((row) => row.textContent?.includes("· English"))).toHaveLength(5);
    await expect(rows.filter((row) => row.textContent?.includes("· Math"))).toHaveLength(5);
    await userEvent.click(canvas.getByRole("button", { name: "Show all 27 courses" }));
    await expect(within(canvas.getByRole("table")).getAllByRole("row")).toHaveLength(28);

    await expect(canvas.getByText(/^Cohort, returned here:/)).toHaveTextContent("Cohort, returned here: 52%");
    await expect(canvas.getByText("−6 pts vs. cohort")).toBeVisible();
    await expect(canvas.getByText("13 students took both in their first term")).toBeVisible();
    await expect(canvas.getByText(/29 first attempts with an incomplete, audit or missing grade are left out/)).toBeVisible();
  },
};

/** Retention set to Back next fall: the same courses, fall to fall retention, and every label says so. */
export const FederalRetention: Story = {
  name: "Back next fall",
  args: { data: gatewayFederal2023 },
  play: async ({ canvas }) => {
    const table = within(canvas.getByRole("table"));
    await expect(table.getByRole("columnheader", { name: "Back next fall if passed" })).toBeVisible();
    const eng = table.getByRole("row", { name: /^ENG 101/ });
    await expect(eng).toHaveTextContent("76%");
    await expect(eng).toHaveTextContent("34%");
    await expect(canvas.getByText(/^Cohort, back next fall:/)).toHaveTextContent("Cohort, back next fall: 42%");
    await expect(canvas.getByText("−34 pts vs. cohort")).toBeVisible();
    await expect(canvas.getByText(/took a course here in Fall 2024, the fall after year 1/)).toBeVisible();
  },
};

/** Fall starters share a first term, so the pairs name it. */
export const FallStarters: Story = {
  name: "Fall starters",
  args: { data: gatewayFall2023 },
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText(/students took both in Fall 2023$/).length).toBeGreaterThan(0);
  },
};

/** The 2024-25 class: its second year is only partly in the data, and the page says so first. */
export const ProvisionalClass: Story = {
  name: "Second year still arriving",
  args: { data: gateway2024 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("note")).toHaveTextContent("The 2024-25 class’s second year is only partly in the data.");
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
