import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Upload } from "lucide-react";
import { expect, fn } from "storybook/test";
import { FileUploadButton } from "./file-upload-button";

// Synthetic file names; nothing here is real PDP data.
const cohortFile = new File(["Student_GUID,Cohort\n"], "cohort.csv", { type: "text/csv" });
const courseFile = new File(["Student_GUID,Course_Prefix\n"], "course.csv", { type: "text/csv" });

/** The hidden file input the button opens. */
function fileInput(canvasElement: HTMLElement) {
  return canvasElement.querySelector<HTMLInputElement>('input[type="file"]')!;
}

/** Counts how often the button opens the picker. Test clicks aren't trusted, so no real dialog opens. */
function countPickerOpens(input: HTMLInputElement) {
  const opens = { count: 0 };
  input.addEventListener("click", () => {
    opens.count += 1;
  });
  return opens;
}

const meta = {
  component: FileUploadButton, title: "Components/UI/File upload button",
  args: { onFiles: fn() },
} satisfies Meta<typeof FileUploadButton>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Choose a CSV file",
  play: async ({ args, canvas, canvasElement, userEvent }) => {
    const input = fileInput(canvasElement);
    const opens = countPickerOpens(input);
    await expect(input).toHaveAttribute("accept", ".csv");
    await expect(input).not.toBeVisible();

    await userEvent.click(canvas.getByRole("button", { name: "Choose file" }));
    await expect(opens.count).toBe(1);

    await userEvent.upload(input, cohortFile);
    await expect(args.onFiles).toHaveBeenCalledWith([cohortFile]);
  },
};

/** Keyboard users open the picker from the visible button with Enter or Space. */
export const FromKeyboard: Story = {
  name: "From the keyboard",
  play: async ({ canvas, canvasElement, userEvent }) => {
    const opens = countPickerOpens(fileInput(canvasElement));
    await userEvent.tab();
    await expect(canvas.getByRole("button", { name: "Choose file" })).toHaveFocus();
    await userEvent.keyboard("{Enter}");
    await userEvent.keyboard(" ");
    await expect(opens.count).toBe(2);
  },
};

/** Cohort and course files picked together, as on the upload screen. */
export const MultipleFiles: Story = {
  name: "Multiple files",
  args: {
    multiple: true,
    variant: "outline",
    children: (
      <>
        <Upload aria-hidden /> Choose files
      </>
    ),
  },
  play: async ({ args, canvasElement, userEvent }) => {
    const input = fileInput(canvasElement);
    await expect(input).toHaveAttribute("multiple");
    await userEvent.upload(input, [cohortFile, courseFile]);
    await expect(args.onFiles).toHaveBeenCalledWith([cohortFile, courseFile]);
  },
};

export const Disabled: Story = {
  args: { disabled: true },
  play: async ({ args, canvas, canvasElement }) => {
    const opens = countPickerOpens(fileInput(canvasElement));
    canvas.getByRole("button", { name: "Choose file" }).click();
    await expect(opens.count).toBe(0);
    await expect(args.onFiles).not.toHaveBeenCalled();
    await expect(canvas.getByRole("button", { name: "Choose file" })).toBeDisabled();
    await expect(fileInput(canvasElement)).toBeDisabled();
  },
};

/** The default label follows the picker mode without overriding custom button content. */
export const MultipleDefaultLabel: Story = {
  name: "Plural label for multiple selection",
  args: { multiple: true },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("button", { name: "Choose files" })).toBeVisible();
  },
};
