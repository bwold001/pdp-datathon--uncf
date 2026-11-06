import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { homeData, homeTools } from "@/components/testing/home-fixtures";
import { WorkbenchStorybookWrapper } from "@/components/testing/workbench-storybook-wrapper";
import { HomePage } from "@/components/workbench/home/home-page";

const firstRun = { uploadHref: "#upload", fieldGuideHref: "#fields", onUseMockData: fn() };
const meta = {
  component: HomePage,
  title: "Workbench/Home/Home page",
  args: { hasData: false, firstRun, tools: { tools: [] } },
  decorators: [(Story, { args }) => (
    <WorkbenchStorybookWrapper page="home" hasData={args.hasData}>
      <Story />
    </WorkbenchStorybookWrapper>
  )],
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof HomePage>;
export default meta;
type Story = StoryObj<typeof HomePage>;

export const FirstRun: Story = {
  name: "First run without team tools",
  play: async ({ canvas, userEvent }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Start with your AR files" })).toBeVisible();
    await expect(canvas.getByRole("link", { name: "Upload AR files" })).toHaveAttribute("href", "#upload");
    await expect(canvas.queryByRole("heading", { name: "Team tools" })).not.toBeInTheDocument();
    await userEvent.click(canvas.getByRole("button", { name: "Try it with the mock data" }));
    await expect(firstRun.onUseMockData).toHaveBeenCalledOnce();
  },
};
export const FirstRunWithTools: Story = {
  name: "First run with team tools",
  args: { tools: homeTools },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Team tools" })).toBeVisible();
    await expect(canvas.getByRole("link", { name: "Ask about students" })).toHaveAttribute("href", "#ask");
  },
};
export const LoadingMockData: Story = {
  args: { firstRun: { ...firstRun, loadingMockData: true } },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Try it with the mock data" })).toBeDisabled();
  },
};
export const DataLoaded: Story = {
  name: "Data loaded without team tools",
  args: { hasData: true, firstRun: undefined, dataLoaded: homeData },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 1, name: "Your data" })).toBeVisible();
    await expect(canvas.getByText("10,313")).toBeVisible();
    await expect(canvas.getByText(/23 warnings from the checks/)).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Try it with the mock data" })).not.toBeInTheDocument();
    await expect(canvas.queryByRole("heading", { name: "Team tools" })).not.toBeInTheDocument();
  },
};
export const DataLoadedWithTools: Story = {
  args: { hasData: true, firstRun: undefined, dataLoaded: homeData, tools: homeTools },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { name: "Team tools" })).toBeVisible();
    await expect(canvas.getByRole("heading", { name: "Start with a question" })).toBeVisible();
  },
};
export const NoStarterQuestions: Story = {
  args: { hasData: true, firstRun: undefined, dataLoaded: { ...homeData, questions: { questions: [] } } },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("heading", { name: "Start with a question" })).not.toBeInTheDocument();
  },
};
export const MobileFirstRun: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("link", { name: "Upload AR files" })).toBeVisible();
    const document = canvasElement.ownerDocument.documentElement;
    await expect(document.scrollWidth).toBeLessThanOrEqual(document.clientWidth);
  },
};
export const MobileDataLoaded: Story = {
  args: DataLoadedWithTools.args,
  globals: { viewport: { value: "mobile1", isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByRole("heading", { name: "Your data" })).toBeVisible();
    const document = canvasElement.ownerDocument.documentElement;
    await expect(document.scrollWidth).toBeLessThanOrEqual(document.clientWidth);
  },
};
