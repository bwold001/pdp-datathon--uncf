import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { ToolCard } from "./tool-card";

const meta = {
  component: ToolCard, title: "Workbench/Home/Tool card",
  args: {
    tag: "Example",
    name: "Ask about students",
    description: "Ask questions in plain language and get an answer about the current group.",
    href: "#ask-about-students",
  },
} satisfies Meta<typeof ToolCard>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Tool card with linked heading",
  play: async ({ canvas, userEvent }) => {
    const link = canvas.getByRole("link", { name: "Ask about students" });
    await expect(canvas.getAllByRole("link")).toHaveLength(1);
    await expect(link).toHaveAttribute("href", "#ask-about-students");
    await expect(canvas.getByRole("heading", { level: 3, name: "Ask about students" })).toBeVisible();
    await userEvent.click(link);
  },
};

/** The dashed card that invites a team to add its own tool. */
export const AddYourTool: Story = {
  name: "Add your tool",
  args: {
    variant: "add",
    tag: "Your team",
    name: "+ Add your tool",
    description: "Register a page with a name and a component. It gets the database and filters.",
    href: "#add-a-tool",
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("link", { name: /Add your tool/ })).toHaveAttribute("data-variant", "add");
  },
};

/** Cards in Home's Team tools section: an h2, then a list of cards. */
export const InTeamToolsSection: Story = {
  name: "In the Team tools section",
  render: () => (
    <section aria-labelledby="team-tools" className="flex max-w-3xl flex-col gap-3">
      <header>
        <h2 id="team-tools" className="text-lg font-medium">Team tools</h2>
        <p className="text-sm text-muted-foreground">Each project team adds its feature here as a card. Cards open the team&apos;s own page.</p>
      </header>
      <ul className="grid gap-3 sm:grid-cols-3">
        <li><ToolCard tag="Needs data" name="Ask about students" description="Ask questions in plain language and get an answer about the current group." href="#ask" /></li>
        <li><ToolCard tag="Needs data" name="Early alert list" description="Students whose year 1 credits and gateway progress suggest they need outreach." href="#alerts" /></li>
        <li><ToolCard variant="add" tag="Your team" name="+ Add your tool" description="Register a page with a name and a component. It gets the database and filters." href="#add" /></li>
      </ul>
    </section>
  ),
  play: async ({ canvas }) => {
    await expect(canvas.getAllByRole("heading", { level: 3 })).toHaveLength(3);
  },
};
