import type { Metadata } from "next";
import { Suspense } from "react";

import { CreditsLoading, CreditsTab } from "@/components/uncf/credits/credits-tab";

export const metadata: Metadata = { title: "Credit momentum" };

/** The Credit momentum tab: is each student making meaningful progress toward a degree? */
export default function CreditMomentumPage() {
  return (
    // The design's heading names the class, so the tab draws it with the numbers; it depends on the cohort bar's URL.
    <Suspense fallback={<CreditsLoading />}>
      <CreditsTab />
    </Suspense>
  );
}
