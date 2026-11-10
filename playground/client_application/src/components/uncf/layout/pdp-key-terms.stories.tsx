import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, spyOn } from "storybook/test";

import { ExplorerStoryFrame } from "./explorer-story-frame";
import { pdpDefinitions } from "./pdp-definitions-fixture";
import { PdpKeyTerms } from "./pdp-key-terms";

const meta = {
  component: PdpKeyTerms,
  title: "UNCF/Explorer layout/Key terms from the dictionary",
  decorators: [
    (Story) => (
      <ExplorerStoryFrame>
        <p>
          <Story />
        </p>
      </ExplorerStoryFrame>
    ),
  ],
  args: { terms: ["retention", "persistence"], children: "Stopped out: no record here or at another college that term." },
  // Answer GET /uncf/definitions with the real dictionary, as the API would.
  beforeEach: () => {
    const spy = spyOn(window, "fetch").mockImplementation(
      async () => new Response(JSON.stringify(pdpDefinitions), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    return () => spy.mockRestore();
  },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PdpKeyTerms>;
export default meta;
type Story = StoryObj<typeof meta>;

/** Retention and persistence in the shared dictionary's words, then the tab's own terms. */
export const RetentionAndPersistence: Story = {
  name: "Retention and persistence",
  play: async ({ canvas }) => {
    await expect(await canvas.findByText("Returned here")).toBeVisible();
    await expect(canvas.getByText("At another college")).toBeVisible();
    await expect(canvas.getByText(/\(PDP Persistence\): enrolled at a different college by the second academic year/)).toBeVisible();
    await expect(canvas.getByText(/Stopped out: no record here or at another college that term\./)).toBeVisible();
  },
};
