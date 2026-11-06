import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { PageIntro } from "@/components/page-intro";
import { sidebarDestinations } from "@/components/testing/navigation-panel-fixtures";
import { NavigationPanel } from "@/components/workbench/navigation-panel/navigation-panel";
import { NumberedStepCard } from "./numbered-step-card";

const firstRunSteps = [
  { title: "Upload", text: "Cohort, course and financial aid files in CSV format." },
  { title: "Check", text: "See problems in plain language before anything is saved." },
  { title: "Explore", text: "Browse students and read what each field means." },
];

const meta = {
  component: NumberedStepCard, title: "Workbench/Home/Numbered step card",
  args: { step: 2, title: "Check", children: "See problems in plain language before anything is saved." },
} satisfies Meta<typeof NumberedStepCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Step number and context",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 3, name: "Check" })).toBeVisible();
    await expect(canvas.getByText("2")).toBeVisible();
  },
};

/** Header, intro and a row of step cards together, as on the home screen before any upload. */
export const OnFirstRunScreen: Story = {
  name: "On the first-run screen",
  render: () => (
    <DashboardShell
      shellTitle="Home"
      leftSidebar={<NavigationPanel destinations={sidebarDestinations} currentPath={sidebarDestinations.home} database={{ status: "empty" }} />}
    >
      <div className="flex max-w-3xl flex-col gap-6 p-6">
        <PageIntro size="sm" eyebrow="No data yet" title="Start with your AR files">
          <p>
            Upload your cohort and course files once. They&apos;re checked against the data dictionary and saved to a
            database on this computer. Nothing leaves your machine.
          </p>
        </PageIntro>
        <ol className="grid gap-3 sm:grid-cols-3">
          {firstRunSteps.map((step, index) => (
            <li key={step.title}>
              <NumberedStepCard step={index + 1} title={step.title}>{step.text}</NumberedStepCard>
            </li>
          ))}
        </ol>
      </div>
    </DashboardShell>
  ),
  parameters: { layout: "fullscreen" },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Start with your AR files" })).toBeVisible();
    await expect(canvas.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent)).toEqual([
      "Upload",
      "Check",
      "Explore",
    ]);
  },
};
