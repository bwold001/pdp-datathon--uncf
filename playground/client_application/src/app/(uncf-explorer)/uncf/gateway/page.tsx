import type { Metadata } from "next";
import { Suspense } from "react";

import { GatewayLoading, GatewayTab } from "@/components/uncf/gateway/gateway-tab";
import { ViewIntro } from "@/components/uncf/layout/view-intro";

export const metadata: Metadata = { title: "Gateway courses" };

/** The Gateway courses tab: how students get through each first-year gateway course, and retention after it. */
export default function GatewayCoursesPage() {
  return (
    <>
      <ViewIntro
        title="Gateway Courses"
        whatThisShows="Every student who took a course the school marks as a gateway course in their first year, counted once per course, from their first try onward."
        howToRead="Pick a course to follow its students. Pick a group in the filters above to compare it with everyone else in each course."
        keyTerms="Passed: a grade of 1.0 or higher, or a Pass, the PDP’s line for gateway courses. The DFW page uses 2.0. Retention: came back the next year."
      >
        How students get through the courses the school marks as gateway courses: on the first try, after retaking, or
        not at all.
      </ViewIntro>
      {/* The numbers depend on the cohort bar, which is in the URL; the intro above renders without it. */}
      <Suspense fallback={<GatewayLoading />}>
        <GatewayTab />
      </Suspense>
    </>
  );
}
