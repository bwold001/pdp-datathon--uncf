import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent } from "storybook/test";

import { buildCsvRows, CSV_COLUMNS, csvFileName, toCsvText } from "./csv";
import { CsvDownloadButton } from "./csv-download-button";
import { loadPathsSample, loadSample, pathsByGender, retentionByGender } from "./explorer-samples";

const meta = {
  component: CsvDownloadButton,
  title: "UNCF/Explorer/CSV download",
  args: { cohort: "2022-23", groupBy: ["pell"], load: loadSample, loadYearTwo: loadPathsSample },
} satisfies Meta<typeof CsvDownloadButton>;
export default meta;
type Story = StoryObj<typeof CsvDownloadButton>;

export const Downloads: Story = {
  play: async ({ canvas }) => {
    await userEvent.click(canvas.getByRole("button", { name: "Download CSV" }));
    await expect(await canvas.findByText(/rows saved to student-success_entered-2022-23_by-pell_SYNTHETIC\.csv/)).toBeVisible();
    await expect(canvas.getByRole("button", { name: /Downloaded/ })).toBeVisible();
  },
};

export const HiddenNumbersAreBlankWithAStatus: Story = {
  play: async () => {
    const rows = buildCsvRows([retentionByGender], pathsByGender);
    const hidden = rows.find((row) => row.measure === "retention" && row.group_value === "X");
    await expect(hidden?.numerator).toBe("");
    await expect(hidden?.rate).toBe("");
    await expect(hidden?.status).toBe("suppressed");
    // Every row says it's synthetic; paths rows also say they're mock.
    await expect(rows.every((row) => row.data_label.startsWith("SYNTHETIC"))).toBe(true);
    await expect(rows.find((row) => row.measure === "year2_path_moved")?.data_label).toContain("MOCK");
    // The rate matches the shown percent: 767 of 1,410 is 54.4%.
    await expect(rows.find((row) => row.measure === "retention" && row.group_value === "F")?.rate).toBe("0.5440");
    const text = toCsvText(rows);
    await expect(text.split("\n")[0]).toBe(CSV_COLUMNS.join(","));
    await expect(csvFileName("2022-23", ["pell", "enrollment_intensity"])).toBe(
      "student-success_entered-2022-23_by-pell-and-enrollment-intensity_SYNTHETIC.csv",
    );
  },
};
