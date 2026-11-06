import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";
import { sidebarDestinations } from "@/components/testing/navigation-panel-fixtures";
import { mockSavedTables } from "@/components/testing/upload-fixtures";
import { UploadSavedCallout } from "./upload-saved-callout";

const meta = {
  component: UploadSavedCallout, title: "Workbench/Upload/Upload saved callout",
  args: { tables: mockSavedTables, joinKey: "Student ID + Cohort", exploreHref: sidebarDestinations.explore },
} satisfies Meta<typeof UploadSavedCallout>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default: Two tables saved to database",
  play: async ({ canvas }) => {
    await expect(canvas.getByRole("heading", { level: 2, name: "Saved" })).toBeVisible();
    await expect(canvas.getByRole("status")).toHaveTextContent(
      "2 tables are in the local database: cohort (10,313 rows) and course (100,951 rows), linked on Student ID + Cohort.",
    );
    await expect(canvas.getByRole("link", { name: "Explore the data" })).toHaveAttribute("href", sidebarDestinations.explore);
  },
};

/** Three synthetic tables use a serial comma and keep each table name bold. */
export const ThreeTables: Story = {
  name: "Three table summary",
  args: { tables: [...mockSavedTables, { name: "holds", rowCount: 10313 }], joinKey: undefined },
  play: async ({ canvas }) => {
    const status = canvas.getByRole("status");
    await expect(status).toHaveTextContent(
      "3 tables are in the local database: cohort (10,313 rows), course (100,951 rows), and holds (10,313 rows).",
    );
    await expect(Array.from(status.querySelectorAll("strong"), (name) => name.textContent)).toEqual([
      "cohort", "course", "holds",
    ]);
  },
};

/** Every save also loads the committed enrichment files, so the callout can say so underneath. */
export const WithEnrichmentNote: Story = {
  name: "With enrichment note",
  args: {
    children: <p>The on-campus housing and institution events files were loaded too.</p>,
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText(/on-campus housing/)).toBeVisible();
  },
};
