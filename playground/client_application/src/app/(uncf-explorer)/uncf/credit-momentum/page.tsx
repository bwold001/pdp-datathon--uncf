import type { Metadata } from "next";
import { Suspense } from "react";

import { CreditsLoading, CreditsTab } from "@/components/uncf/credits/credits-tab";
import { ViewIntro } from "@/components/uncf/layout/view-intro";

export const metadata: Metadata = { title: "Credit momentum" };

/** The Credit momentum tab: first-year credits, milestones, and retention by credits earned. */
export default function CreditMomentumPage() {
  return (
    <>
      <ViewIntro
        title="Credit Momentum"
        whatThisShows="How quickly the selected cohort builds credits during the first year."
        howToRead="Longer bars = more students reaching each milestone. The tier table compares next-fall retention by credits earned."
        keyTerms="Credit completion ratio: credits earned ÷ credits attempted. 30 credits in year 1: on pace for a 4-year degree."
      >
        First-year credits attempted and earned, and progress toward the 12, 24 and 30-credit milestones.
      </ViewIntro>
      {/* The numbers depend on the cohort bar, which is in the URL; the intro above renders without it. */}
      <Suspense fallback={<CreditsLoading />}>
        <CreditsTab />
      </Suspense>
    </>
  );
}
