import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, waitFor } from "storybook/test";

import { loadSample } from "@/components/uncf/explorer/explorer-samples";

import { CardMaker } from "./card-maker";

const meta = {
  component: CardMaker,
  title: "UNCF/Insight card/Card maker",
  args: { cohort: "2022-23", groupBy: ["pell"], initialMeasure: "retention", load: loadSample },
} satisfies Meta<typeof CardMaker>;
export default meta;
type Story = StoryObj<typeof CardMaker>;

/** Replace the takeaway with new text. */
async function type(canvas: Parameters<NonNullable<Story["play"]>>[0]["canvas"], text: string) {
  const box = await canvas.findByRole("textbox", { name: /one-sentence takeaway/i });
  await userEvent.clear(box);
  if (text) await userEvent.type(box, text);
}

export const SuggestedSentencePasses: Story = {
  play: async ({ canvas }) => {
    await expect(await canvas.findByText(/Ready: choose/)).toBeVisible();
    await expect(canvas.getByRole("article", { name: "Insight card" })).toHaveTextContent("58.9% of Pell grant recipients");
  },
};

export const SwappedGroupsAreCaught: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "Students without a Pell grant came back at 58.9%, compared with 53.7% for Pell grant recipients.");
    await expect(await canvas.findByText(/58\.9% isn't the rate for No Pell grant on the card/)).toBeVisible();
    await expect(canvas.getByText(/Fix 1 check to save/)).toBeVisible();
  },
};

export const WrongGapIsCaught: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "Pell grant recipients came back at 58.9% vs 53.7% without Pell, a 12-point gap.");
    await expect(await canvas.findByText(/is 5\.2 points, not 12/)).toBeVisible();
  },
};

export const CauseAndDeficitWordsAreCaught: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "Pell aid drives a 58.9% return rate while students without Pell dropped out.");
    await expect(await canvas.findByText(/Remove “drives”/)).toBeVisible();
    await expect(canvas.getByText(/Replace “dropped out”/)).toBeVisible();
  },
};

export const SmallCountsAreCaught: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "Just 2 of the Pell grant recipients came back, 58.9% overall.");
    await expect(await canvas.findByText(/Small counts like 2/)).toBeVisible();
  },
};

export const EmptyShowsAPlaceholder: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "");
    await expect(await canvas.findByText("Your one-sentence takeaway goes here.")).toBeVisible();
    await expect(canvas.getByRole("button", { name: /Save as PDF/ })).toHaveAttribute("aria-disabled", "true");
  },
};

export const DraftsSurviveTabSwitches: Story = {
  play: async ({ canvas }) => {
    await type(canvas, "My draft: 58.9% of Pell grant recipients came back.");
    await userEvent.click(canvas.getByRole("button", { name: "Gateway math" }));
    await waitFor(() => expect(canvas.getByRole("article", { name: "Insight card" })).toHaveTextContent("GATEWAY MATH"));
    await userEvent.click(canvas.getByRole("button", { name: "Returned here" }));
    await expect(await canvas.findByDisplayValue("My draft: 58.9% of Pell grant recipients came back.")).toBeVisible();
  },
};
