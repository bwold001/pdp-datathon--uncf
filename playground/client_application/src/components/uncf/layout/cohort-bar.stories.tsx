import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { getRouter } from "@storybook/nextjs-vite/navigation.mock";
import { useState } from "react";
import { expect, fn, waitFor, within } from "storybook/test";

import { cohortOptions2023 } from "@/components/uncf/paths/paths-fixtures";

import { CohortBar, CohortBarView } from "./cohort-bar";
import { cohortFiltersFor, defaultCohortFilters } from "./cohort-filters";
import { cohortFilters } from "./explorer-config";
import { ExplorerProvider, useExplorer, useShowStudentCount } from "./explorer-context";
import { ExplorerStoryFrame } from "./explorer-story-frame";
import { FilterSheet } from "./filter-menu";
import { useExplorerResource } from "./use-explorer-resource";

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

const paths = cohortFiltersFor("/uncf/paths");
const sheetChange = fn();
const sheetClearAll = fn();

/** Add filter lists the filters by group; a pick goes into the URL, keeping the page's own query values. */
export const AddAFilter: Story = {
  name: "Add a filter",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw", query: { sort: "rate" } } } },
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("button", { name: "Add filter" }));
    await expect(await page.findByRole("group", { name: "Financial aid" })).toBeVisible();
    await userEvent.click(page.getByRole("button", { name: /^Pell \(year 1\)/ }));
    await userEvent.click(await page.findByRole("button", { name: /^Pell recipient/ }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/dfw?pell=Y&sort=rate", { scroll: false });
  },
};

/** Each filter set is a chip: × removes it, and Clear filters removes them all but keeps the class year and enrollment type. */
export const ChipsAndClearAll: Story = {
  name: "Chips and Clear filters",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw", query: { cohort: "2022-23", pell: "Y", race: "Asian" } } } },
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByRole("button", { name: "Remove Pell recipient" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Remove Asian" }));
    await expect(getRouter().push).toHaveBeenLastCalledWith("/uncf/dfw?cohort=2022-23&pell=Y", { scroll: false });
    await userEvent.click(canvas.getByRole("button", { name: "Clear filters" }));
    await expect(getRouter().push).toHaveBeenLastCalledWith("/uncf/dfw?cohort=2022-23", { scroll: false });
  },
};

/** With nothing added, the bar is one line: no chips, no Clear filters. */
export const NothingAdded: Story = {
  name: "Nothing added",
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: /^Remove / })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("button", { name: "Clear filters" })).not.toBeInTheDocument();
  },
};

/** Student paths follows first-time students, as in the design; the sentence says so and All is one pick away. */
export const PathsStartsAtFirstTime: Story = {
  name: "Student paths starts at first-time",
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    const picker = canvas.getByRole("button", { name: "Enrollment type: First-time" });
    await expect(picker).toHaveTextContent("first-time");
    await userEvent.click(picker);
    await userEvent.click(await page.findByRole("button", { name: "Every enrollment type" }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/paths?enrollment_type=all", { scroll: false });
  },
};

/** Every other tab counts every enrollment type, and the sentence says so. */
export const OtherTabsCountEveryType: Story = {
  name: "Other tabs count every type",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/gateway" } } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Enrollment type: All" })).toHaveTextContent("of every enrollment type");
  },
};

/** Gateway and Credit momentum show the retention measure beside Add filter, starting at the PDP flag; it has no "All". */
export const PickTheRetentionMeasure: Story = {
  name: "Pick the retention measure",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/gateway" } } },
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    const picker = canvas.getByRole("button", { name: "Retention: Returned here" });
    await userEvent.click(picker);
    await expect(page.queryByRole("button", { name: /^Any/ })).not.toBeInTheDocument();
    await userEvent.click(await page.findByRole("button", { name: "Back next fall" }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/gateway?retention_type=federal", { scroll: false });
  },
};

/** Student paths and DFW don't report retention, so they don't show it. */
export const RetentionOnlyWhereUsed: Story = {
  name: "Retention only where it's used",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw" } } },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: /^Retention:/ })).not.toBeInTheDocument();
  },
};

/** Clear filters keeps what this tab doesn't show (a retention measure set on Gateway) and the page's own values. */
export const ClearAllKeepsHiddenFilters: Story = {
  name: "Clear filters keeps filters other tabs show",
  parameters: {
    nextjs: { appDirectory: true, navigation: { pathname: "/uncf/dfw", query: { pell: "Y", retention_type: "federal", sort: "rate" } } },
  },
  play: async ({ canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Clear filters" }));
    await expect(getRouter().push).toHaveBeenCalledWith("/uncf/dfw?retention_type=federal&sort=rate", { scroll: false });
  },
};

/** A value the filter doesn't offer, from an old or hand-edited link, is ignored. */
export const IgnoresAnUnknownValue: Story = {
  name: "Ignores an unknown value",
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/paths", query: { pell: "maybe" } } } },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: /^Remove / })).not.toBeInTheDocument();
  },
};

/** With the API's counts (real, for 2023-24): the sentence counts the tab's students, and groups under 10 can't be picked. */
export const WithCounts: Story = {
  name: "With counts",
  render: () => <CohortBarView definitions={paths} filters={defaultCohortFilters(paths)} options={cohortOptions2023} studentCount={1114} />,
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByText("1,114").parentElement).toHaveTextContent("1,114 first-time students who entered in 2023-24");
    await userEvent.click(canvas.getByRole("button", { name: "Add filter" }));
    await userEvent.click(await page.findByRole("button", { name: /^Gender/ }));
    await expect(await page.findByRole("button", { name: "Prefer not to specify 0" })).toBeDisabled();
    await userEvent.click(page.getByRole("button", { name: "All filters" }));
    await userEvent.click(page.getByRole("button", { name: /^Race/ }));
    await expect(await page.findByRole("button", { name: "Native Hawaiian or Other Pacific Islander under 10" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Asian 196" })).toBeEnabled();
  },
};

/** When the tab hides its numbers for too few students, the sentence says so, not the whole class's size. */
export const FewerThanTen: Story = {
  name: "Fewer than 10 match",
  render: () => (
    <CohortBarView definitions={paths} filters={{ ...defaultCohortFilters(paths), pell: "Y", race: "Asian" }} options={cohortOptions2023} studentCount="too few" />
  ),
  play: async ({ canvas }) => {
    await expect(canvas.getByText("Fewer than 10")).toBeVisible();
    await expect(canvas.queryByText(/2,580/)).not.toBeInTheDocument();
  },
};

/** With UNCF_MIN_STUDENTS unset (1), nothing is hidden: no ⓘ about hidden groups, and an empty value reads "none". */
export const SmallGroupsShown: Story = {
  name: "Small groups shown",
  render: () => <CohortBarView definitions={paths} filters={defaultCohortFilters(paths)} options={{ ...cohortOptions2023, min_students: 1 }} studentCount={1114} />,
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByText("1,114").parentElement).toHaveTextContent("1,114 first-time students who entered in 2023-24");
    await expect(canvas.queryByRole("button", { name: "About hidden groups" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Add filter" }));
    await userEvent.click(await page.findByRole("button", { name: /^Race/ }));
    await expect(await page.findByRole("button", { name: "Native Hawaiian or Other Pacific Islander none" })).toBeDisabled();
  },
};

/** On a phone, one Filters button opens every filter in a sheet; a pick applies at once and goes back to the list, Done closes it. */
export const PhoneSheet: Story = {
  name: "Phone sheet",
  render: () => (
    <FilterSheet
      definitions={cohortFilters.filter((definition) => definition.place === "menu")}
      filters={{ ...defaultCohortFilters(), pell: "Y" }}
      counts={cohortOptions2023.filters}
      onChange={sheetChange}
      countsNote="Counts are the 2023-24 class’s students with each value, before other filters."
      summary="594 first-time students who entered in 2023-24"
      activeCount={1}
      onClearAll={sheetClearAll}
    />
  ),
  play: async ({ canvas, canvasElement, userEvent }) => {
    const page = within(canvasElement.ownerDocument.body);
    await userEvent.click(canvas.getByRole("button", { name: "Filters · 1" }));
    const sheet = await page.findByRole("dialog", { name: "Filters" });
    await expect(within(sheet).getByText("594 first-time students who entered in 2023-24")).toBeVisible();
    await expect(within(sheet).getByRole("button", { name: /^Pell \(year 1\)/ })).toHaveTextContent("Pell recipient");
    await userEvent.click(within(sheet).getByRole("button", { name: /^Gender/ }));
    await userEvent.click(within(sheet).getByRole("button", { name: /^Female/ }));
    await expect(sheetChange).toHaveBeenCalledWith("gender", "F");
    await expect(within(sheet).getByRole("group", { name: "Demographics" })).toBeVisible();
    await userEvent.click(within(sheet).getByRole("button", { name: "Clear filters" }));
    await expect(sheetClearAll).toHaveBeenCalled();
    await userEvent.click(within(sheet).getByRole("button", { name: "Done" }));
    // The sheet stays mounted while it animates closed.
    await waitFor(() => expect(page.queryByRole("dialog", { name: "Filters" })).not.toBeInTheDocument());
  },
};

// The Pell answer, held until the story lets it arrive.
let sendPellAnswer: (students: number) => void = () => {};
const everyoneAnswer = () => Promise.resolve(1114);
const pellAnswer = () => new Promise<number>((resolve) => (sendPellAnswer = resolve));

/** A tab that loads its count like the real ones, and a button that adds Pell as the bar's "Add filter" would. */
function TabWithSlowAnswer() {
  const [pell, setPell] = useState(false);
  const { resource, current } = useExplorerResource(pell ? pellAnswer : everyoneAnswer);
  useShowStudentCount(resource.status !== "success" || !current ? null : resource.data);
  const { studentCount } = useExplorer();
  const filters = { ...defaultCohortFilters(paths), pell: pell ? "Y" : null };
  return (
    <>
      <CohortBarView definitions={paths} filters={filters} options={cohortOptions2023} studentCount={studentCount} />
      <button type="button" onClick={() => setPell(true)}>
        Add Pell
      </button>
    </>
  );
}

/** While the new filters' answer loads, the sentence drops the last filters' count instead of pairing it with them. */
export const CountWhileNewFiltersLoad: Story = {
  name: "Count while new filters load",
  render: () => <TabWithSlowAnswer />,
  play: async ({ canvas, userEvent }) => {
    const sentence = () => canvas.getByText(/who entered in/).closest("p");
    await waitFor(() => expect(sentence()).toHaveTextContent("1,114 first-time students who entered in 2023-24"));
    await userEvent.click(canvas.getByRole("button", { name: "Add Pell" }));
    await expect(canvas.getByRole("button", { name: "Remove Pell recipient" })).toBeVisible();
    await expect(sentence()).not.toHaveTextContent("1,114");
    await expect(sentence()).toHaveTextContent("Showing first-time students who entered in 2023-24");
    sendPellAnswer(594);
    await waitFor(() => expect(sentence()).toHaveTextContent("594 first-time students who entered in 2023-24"));
  },
};
