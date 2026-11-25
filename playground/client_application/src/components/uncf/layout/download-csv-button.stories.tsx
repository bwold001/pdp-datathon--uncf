import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect } from "storybook/test";

import { env } from "@/lib/env";

import { DownloadCsvButton } from "./download-csv-button";
import { ExplorerStoryFrame } from "./explorer-story-frame";

const meta = {
  component: DownloadCsvButton,
  title: "UNCF/Explorer layout/Download CSV",
  decorators: [
    (Story) => (
      <ExplorerStoryFrame>
        <Story />
      </ExplorerStoryFrame>
    ),
  ],
  args: { path: "/uncf/gateway" },
  parameters: { nextjs: { appDirectory: true, navigation: { pathname: "/uncf/gateway" } } },
} satisfies Meta<typeof DownloadCsvButton>;
export default meta;
type Story = StoryObj<typeof meta>;

/** With no filters picked, the link asks for the page's default cohort and retention measure as CSV. */
export const Defaults: Story = {
  play: async ({ canvas }) => {
    const link = canvas.getByRole("link", { name: "Download CSV" });
    const href = new URL(link.getAttribute("href") ?? "", "http://localhost");
    await expect(href.pathname).toBe(new URL(`${env.apiBaseUrl}/uncf/gateway`, "http://localhost").pathname);
    await expect(href.searchParams.get("format")).toBe("csv");
    await expect(href.searchParams.get("cohort")).toBeTruthy();
    await expect(link).toHaveAttribute("download");
  },
};

/** The cohort bar's picks in the URL go into the CSV request, so the file matches what the page shows. */
export const WithFilters: Story = {
  parameters: {
    nextjs: {
      appDirectory: true,
      navigation: { pathname: "/uncf/gateway", query: { cohort: "2022-23", pell: "Y", retention_type: "federal" } },
    },
  },
  play: async ({ canvas }) => {
    const href = new URL(canvas.getByRole("link", { name: "Download CSV" }).getAttribute("href") ?? "", "http://localhost");
    await expect(href.searchParams.get("cohort")).toBe("2022-23");
    await expect(href.searchParams.get("pell")).toBe("Y");
    await expect(href.searchParams.get("retention_type")).toBe("federal");
    await expect(href.searchParams.get("format")).toBe("csv");
  },
};
