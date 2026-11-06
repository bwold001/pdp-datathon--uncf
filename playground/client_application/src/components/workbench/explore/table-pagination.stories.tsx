import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn } from "storybook/test";
import { TablePagination } from "@/components/workbench/explore/table-pagination";
const meta = { component: TablePagination, title: "Workbench/Explore/Table pagination", args: { pageIndex: 0, pageSize: 25, totalRows: 10313, onPrevious: fn(), onNext: fn() } } satisfies Meta<typeof TablePagination>;
export default meta;
type Story = StoryObj<typeof meta>;
export const FirstPage: Story = {
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("1–25 of 10,313 students");
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
    await userEvent.click(canvas.getByRole("button", { name: "Next" }));
    await expect(args.onNext).toHaveBeenCalledOnce();
  },
};
export const LastPage: Story = {
  args: { pageIndex: 412 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("status")).toHaveTextContent("10,301–10,313 of 10,313 students");
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
  },
};
export const NoStudents: Story = {
  args: { totalRows: 0 },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Previous" })).toBeDisabled();
  },
};
