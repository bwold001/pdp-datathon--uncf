import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, waitFor } from "storybook/test";
import { FileDropzone } from "./file-dropzone";

// Synthetic file names; nothing here is real PDP data.
const cohortFile = new File(["Student_GUID,Cohort\n"], "cohort.csv", { type: "text/csv" });
const courseFile = new File(["Student_GUID,Course_Prefix\n"], "course.csv", { type: "text/csv" });
const notesFile = new File(["notes"], "notes.txt", { type: "text/plain" });

/** Fires a file drag event and returns false when its default was prevented. */
function drag(target: Element, type: "dragover" | "drop", files: File[]) {
  const dataTransfer = new DataTransfer();
  files.forEach((file) => dataTransfer.items.add(file));
  return target.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer }));
}

const meta = {
  component: FileDropzone, title: "Workbench/Upload/File dropzone",
  args: { onFiles: fn(), onRejectedFiles: fn(), onUseMockFiles: fn() },
} satisfies Meta<typeof FileDropzone>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Choose mock upload files",
  play: async ({ args, canvas, userEvent }) => {
    await expect(canvas.getByRole("heading", { level: 2, name: "Drop CSV files here" })).toBeVisible();
    await userEvent.click(canvas.getByRole("button", { name: "Use the mock files" }));
    await expect(args.onUseMockFiles).toHaveBeenCalledOnce();
  },
};

/** Dropped CSVs go to onFiles; anything else goes to onRejectedFiles so the page can explain. */
export const DropFiles: Story = {
  name: "Drop files",
  play: async ({ args, canvas, canvasElement }) => {
    const zone = canvasElement.querySelector<HTMLElement>('[data-slot="empty"]')!;
    await expect(drag(zone, "dragover", [cohortFile])).toBe(false);
    // dragover is a continuous event, so React applies its state change on the next render, not at once
    await waitFor(() => expect(zone).toHaveAttribute("data-dragging"));
    drag(zone, "drop", [cohortFile, courseFile, notesFile]);
    await waitFor(() => expect(zone).not.toHaveAttribute("data-dragging"));
    await expect(args.onFiles).toHaveBeenCalledWith([cohortFile, courseFile]);
    await expect(args.onRejectedFiles).toHaveBeenCalledWith([notesFile]);
    await expect(canvas.getByRole("button", { name: "Choose files" })).toBeEnabled();
  },
};

/** While a check runs, nothing new can be added. */
export const Disabled: Story = {
  name: "Disabled zone ignores file drags and drops",
  args: { disabled: true },
  play: async ({ args, canvas, canvasElement }) => {
    await expect(canvas.getByRole("button", { name: "Choose files" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Use the mock files" })).toBeDisabled();
    const zone = canvasElement.querySelector('[data-slot="empty"]')!;
    await expect(drag(zone, "dragover", [cohortFile])).toBe(true);
    await expect(zone).not.toHaveAttribute("data-dragging");
    drag(zone, "drop", [cohortFile, notesFile]);
    await expect(args.onFiles).not.toHaveBeenCalled();
    await expect(args.onRejectedFiles).not.toHaveBeenCalled();
  },
};

/** Without onUseMockFiles, as on the upload page once data is loaded, only Choose files shows. */
export const WithoutMockFiles: Story = {
  name: "No mock data fallback",
  args: { onUseMockFiles: undefined },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole("button", { name: "Use the mock files" })).toBeNull();
  },
};

/** The picker's type filter is only a hint, so a picked non-CSV is rejected the same way a dropped one is. */
export const PickFiles: Story = {
  name: "Pick files",
  play: async ({ args, canvasElement }) => {
    const input = canvasElement.querySelector<HTMLInputElement>('input[type="file"]')!;
    const picked = new DataTransfer();
    [cohortFile, notesFile].forEach((file) => picked.items.add(file));
    input.files = picked.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
    await expect(args.onFiles).toHaveBeenCalledWith([cohortFile]);
    await expect(args.onRejectedFiles).toHaveBeenCalledWith([notesFile]);
  },
};

/** MIME matching uses file metadata, even when a file has a different extension. */
export const AcceptCsvMimeType: Story = {
  name: "Accept CSV MIME type",
  args: { accept: " TEXT/CSV " },
  play: async ({ args, canvasElement }) => {
    const csvFile = new File(["synthetic"], "export.bin", { type: "text/csv" });
    drag(canvasElement.querySelector('[data-slot="empty"]')!, "drop", [csvFile, notesFile]);
    await expect(args.onFiles).toHaveBeenCalledWith([csvFile]);
    await expect(args.onRejectedFiles).toHaveBeenCalledWith([notesFile]);
  },
};

/** Mixed entries ignore empty tokens and match extensions without MIME metadata. */
export const AcceptExtensionsAndMimeWildcards: Story = {
  name: "Accept extensions and MIME wildcards",
  args: { accept: " .CSV, , IMAGE/*, " },
  play: async ({ args, canvasElement }) => {
    const csvFile = new File(["synthetic"], "COHORT.CSV");
    const imageFile = new File(["synthetic"], "image.bin", { type: "image/png" });
    const unknownFile = new File(["synthetic"], "unknown.bin");
    drag(canvasElement.querySelector('[data-slot="empty"]')!, "drop", [csvFile, imageFile, notesFile, unknownFile]);
    await expect(args.onFiles).toHaveBeenCalledWith([csvFile, imageFile]);
    await expect(args.onRejectedFiles).toHaveBeenCalledWith([notesFile, unknownFile]);
  },
};

/** Empty accept allows files regardless of extension or MIME metadata. */
export const AcceptAllFileTypes: Story = {
  name: "Accept all file types",
  args: { accept: "" },
  play: async ({ args, canvasElement }) => {
    const unknownFile = new File(["synthetic"], "unknown.bin");
    drag(canvasElement.querySelector('[data-slot="empty"]')!, "drop", [cohortFile, notesFile, unknownFile]);
    await expect(args.onFiles).toHaveBeenCalledWith([cohortFile, notesFile, unknownFile]);
    await expect(args.onRejectedFiles).not.toHaveBeenCalled();
  },
};
