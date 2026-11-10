import type { Metadata } from "next";
import { Suspense } from "react";

import { DfwLoading, DfwPage as DfwTab } from "@/components/uncf/dfw/dfw-page";
import { ViewIntro } from "@/components/uncf/layout/view-intro";

export const metadata: Metadata = { title: "DFW" };

/** The DFW tab: which courses students don't pass, and for which groups. */
export default function DfwPage() {
  return (
    <>
      <ViewIntro
        title="DFW"
        whatThisShows="Every time a student finishes a course with a final grade, it counts once. This page shows how often that grade was a D, F or W, and in which courses."
        howToRead="Pick a course on the left. On the right, each student group in that course is compared with everyone else in the same course."
        keyTerms="DFW rate: the share of final grades that were a D, F or W. Anything below a C counts, including a C minus. W: the student withdrew."
      >
        Which courses students don’t pass, and which students that hits hardest. Students who entered in the selected
        cohort, in every term they took courses.
      </ViewIntro>
      {/* The numbers depend on the cohort bar, which is in the URL; the intro above renders without it. */}
      <Suspense fallback={<DfwLoading />}>
        <DfwTab />
      </Suspense>
    </>
  );
}
