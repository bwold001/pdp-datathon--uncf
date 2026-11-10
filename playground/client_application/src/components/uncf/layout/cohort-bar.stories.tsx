import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { getRouter } from "@storybook/nextjs-vite/navigation.mock";
import { expect, within } from "storybook/test";

import { cohortOptions2023 } from "@/components/uncf/paths/paths-fixtures";

import { CohortBar, CohortBarView } from "./cohort-bar";
import { defaultCohortFilters } from "./cohort-filters";
import { ExplorerProvider } from "./explorer-context";
import { ExplorerStoryFrame } from "./explorer-story-frame";

const meta = {
  component: CohortBar,
  title: "UNCF/Explorer layout/Cohort bar",
  decorators: [
    (Story) => (
      <ExplorerProvider>
        <ExplorerStoryFrame padded={false}>
          <Story />
        </ExplorerStoryFrame>
      </ExplorerProvider>
    ),
  ],
  parameters: {
    layout: "fullscreen",
    // Storybook merges story parameters into these, so each story sets its own query.
    nextjs: { appDirectory: true, navigation: { pathname: "/uncf/paths" } },
  },
} satisfies Meta<typeof CohortBar>;
export default meta;
type Story = StoryObj<typeof meta>;

/** A pick only counts once Apply is pressed; then it goes into the URL, keeping the page's own query values. */
export const ApplyAFilter: Story = {
  name: "Apply a filter",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw", query: { sort: "rate" } } } },
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("button", { name: /^Pell \(year 1\)/ }));
    await userEvent.click(await page.findByRole("radio", { name: /^Pell recipient/ }));
    await expect(getRouter().push).not.toHaveBeenCalled();
    await userEvent.click(page.getByRole("button", { name: "Apply" }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/dfw?pell=Y&sort=rate", { scroll: false });
  },
};

/** Reset puts every filter back to its default. */
export const Reset: Story = {
  parameters: {
    nextjs: { appDirectory: true, navigation: { pathname: "/uncf/paths", query: { cohort: "2022-23", race: "Asian" } } },
  },
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByText(/· 2 filters set$/)).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Reset" }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/paths", { scroll: false });
  },
};

/** A value the filter doesn't offer, from an old or hand-edited link, is ignored. */
export const IgnoresAnUnknownValue: Story = {
  name: "Ignores an unknown value",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/paths", query: { pell: "maybe" } } } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: /^Pell \(year 1\)/ })).toHaveTextContent("All");
  },
};

/** With the API's counts (real, for 2023-24): each value shows its students, and groups under 10 can't be picked. */
export const WithCounts: Story = {
  name: "With counts",
  render: () => <CohortBarView filters={defaultCohortFilters()} options={cohortOptions2023} studentCount={1114} />,
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByText("Showing 1,114 students")).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: /^Pell \(year 1\)/ }));
    await expect(await page.findByRole("radio", { name: "Pell recipient 873" })).toBeEnabled();
    await userEvent.keyboard("{Escape}");
    await userEvent.click(canvas.getByRole("button", { name: /^Gender/ }));
    await expect(await page.findByRole("radio", { name: "Prefer not to specify 0" })).toBeDisabled();
    await userEvent.keyboard("{Escape}");
    await userEvent.click(canvas.getByRole("button", { name: /^Race/ }));
    await expect(await page.findByRole("radio", { name: "Native Hawaiian or Other Pacific Islander under 10" })).toBeDisabled();
  },
};

/** Searching a long list narrows it. */
export const SearchALongList: Story = {
  name: "Search a long list",
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("button", { name: /^Race/ }));
    await userEvent.type(await page.findByRole("searchbox", { name: "Search Race" }), "his");
    await expect(page.getByRole("radio", { name: /^Hispanic/ })).toBeVisible();
    await expect(page.queryByRole("radio", { name: /^White/ })).not.toBeInTheDocument();
  },
};
