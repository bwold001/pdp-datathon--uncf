import type { Metadata } from "next";
import { Suspense } from "react";

import { GatewayLoading, GatewayTab } from "@/components/uncf/gateway/gateway-tab";
import { ViewIntro } from "@/components/uncf/layout/view-intro";

export const metadata: Metadata = { title: "Gateway courses" };

/** The Gateway courses tab: first-year math and English outcomes, and retention after them. */
export default function GatewayCoursesPage() {
  return (
    <>
      <ViewIntro
        title="Gateway Course Outcomes"
        whatThisShows="Results of each student’s first attempt at a gateway course in year 1."
        howToRead="Each bar totals 100%. The gap between the two retention columns shows how much passing the course matters."
        keyTerms="Gateway course: first college-level math or English, flagged in PDP. D/F/W: a grade of D or F, or a withdrawal."
      >
        Pass, D/F and withdrawal rates in first-year math and English, and their relationship to next-fall retention.
      </ViewIntro>
      {/* The numbers depend on the cohort bar, which is in the URL; the intro above renders without it. */}
      <Suspense fallback={<GatewayLoading />}>
        <GatewayTab />
      </Suspense>
    </>
  );
}
