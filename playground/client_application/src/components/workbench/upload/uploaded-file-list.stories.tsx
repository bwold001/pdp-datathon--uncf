import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { financialAidNote, mockUploadedFiles } from "@/components/testing/upload-fixtures";
import { createUploadedFile, UploadedFileList } from "./uploaded-file-list";

const meta = {
  component: UploadedFileList, title: "Workbench/Upload/Uploaded file list",
  args: { files: mockUploadedFiles, note: financialAidNote },
} satisfies Meta<typeof UploadedFileList>;
export default meta;
type Story = StoryObj<typeof meta>;

/** Both files read and checked, with sizes. */
export const Checked: Story = {
  name: "Checked upload list",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("list", { name: "Uploaded files" }).children).toHaveLength(2);
    await expect(canvas.getByText("10,313 rows · 85 columns")).toBeVisible();
    await expect(canvas.getAllByText("Checked")).toHaveLength(2);
    await expect(canvas.getByText(financialAidNote)).toBeVisible();
  },
};

/** Right after the files are chosen: sizes aren't known yet and each row shows a spinner. */
export const Checking: Story = {
  name: "Files being checked",
  args: {
    files: mockUploadedFiles.map(({ id, name, kind }) => ({ id, name, kind, status: "checking" as const })),
    note: undefined,
  },
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText("Checking…")).toHaveLength(2);
    await expect(canvas.queryByText(/rows ·/)).toBeNull();
  },
};

/** Two files with the same name, which the check refuses, still show as two rows. */
export const SameFileName: Story = {
  name: "Duplicate files remain separate rows",
  args: { files: [mockUploadedFiles[0], { ...mockUploadedFiles[1], name: mockUploadedFiles[0].name }], note: undefined },
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText(mockUploadedFiles[0].name)).toHaveLength(2);
  },
};

/** Exercises entry identity independently of names, positions, and validation status. */
function FileIdentityExample() {
  const [files, setFiles] = useState(() => [
    createUploadedFile(new File(["synthetic cohort"], "data.csv"), "Cohort"),
    createUploadedFile(new File(["synthetic course"], "data.csv"), "Course"),
  ]);

  return (
    <>
      <button onClick={() => setFiles((current) => [...current].reverse())}>Reverse files</button>
      <button onClick={() => setFiles((current) => current.slice(1))}>Remove first file</button>
      <button onClick={() => setFiles((current) => current.map((file) => ({ ...file, name: "renamed.csv" })))}>Rename files</button>
      <button onClick={() => setFiles((current) => current.map((file) => ({ ...file, status: "saved" })))}>Mark saved</button>
      <button onClick={() => setFiles((current) => current.map((file) => createUploadedFile(new File(["replacement"], file.name), file.kind)))}>Replace files</button>
      <UploadedFileList files={files} />
    </>
  );
}

/** Same-named entries keep their DOM identity through edits; replacing a file starts a new entry. */
export const StableEntryIdentity: Story = {
  render: () => <FileIdentityExample />,
  play: async ({ canvas, userEvent }) => {
    const list = canvas.getByRole("list", { name: "Uploaded files" });
    const cohortRow = canvas.getByText("Cohort").closest("li");
    const courseRow = canvas.getByText("Course").closest("li");

    await userEvent.click(canvas.getByRole("button", { name: "Reverse files" }));
    await expect(list.children[0]).toBe(courseRow);
    await expect(list.children[1]).toBe(cohortRow);

    await userEvent.click(canvas.getByRole("button", { name: "Remove first file" }));
    await expect(list.children).toHaveLength(1);
    await expect(list.children[0]).toBe(cohortRow);

    await userEvent.click(canvas.getByRole("button", { name: "Rename files" }));
    await expect(canvas.getByText("renamed.csv")).toBeVisible();
    await expect(list.children[0]).toBe(cohortRow);

    await userEvent.click(canvas.getByRole("button", { name: "Mark saved" }));
    await expect(canvas.getByText("Saved")).toBeVisible();
    await expect(list.children[0]).toBe(cohortRow);

    await userEvent.click(canvas.getByRole("button", { name: "Replace files" }));
    await expect(canvas.getByText("renamed.csv")).toBeVisible();
    await expect(canvas.getByText("Checking…")).toBeVisible();
    await expect(list.children[0]).not.toBe(cohortRow);
  },
};

export const Saved: Story = {
  name: "Saved upload list",
  args: { files: mockUploadedFiles.map((file) => ({ ...file, status: "saved" as const })), note: undefined },
  play: async ({ canvas }) => {
    await expect(canvas.getAllByText("Saved")).toHaveLength(2);
  },
};
