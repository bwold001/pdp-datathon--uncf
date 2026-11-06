import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Badge } from "./badge";
const meta = { component: Badge, title: "Components/UI/Badge", args: { children: "Cohort" } } satisfies Meta<typeof Badge>;
export default meta;
type Story = StoryObj<typeof meta>;
export const Default: Story = { name: "Default badge",};
export const Outline: Story = { name: "Outline badge", args: { variant: "outline" } };
export const Secondary: Story = { name: "Secondary badge", args: { variant: "secondary" } };
