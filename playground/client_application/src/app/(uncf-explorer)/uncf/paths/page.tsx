import type { Metadata } from "next";
import { Suspense } from "react";

import { PdpKeyTerms } from "@/components/uncf/layout/pdp-key-terms";
import { ViewIntro } from "@/components/uncf/layout/view-intro";
import { PathsLoading, StudentPaths } from "@/components/uncf/paths/student-paths";

export const metadata: Metadata = { title: "Student paths" };

/** The Student paths tab: where the entering cohort is, term by term. */
export default function StudentPathsPage() {
  return (
    <>
      <ViewIntro
        title="Student Paths"
        whatThisShows="The selected entering cohort’s students (first-time unless you pick another enrollment type), followed through their next two fall or spring terms."
        howToRead="Band width = number of students. Bands split where students leave or transfer, and rejoin when they return."
        keyTerms={
          // Retention and persistence in the shared dictionary's words (measures/definitions.py), as /definitions sends them.
          <PdpKeyTerms terms={["retention", "persistence"]}>
            <b className="font-semibold">Earned a credential:</b> no course here that term, but earned a credential here in an earlier year.{" "}
            <b className="font-semibold">Stopped out:</b> no record here or at another college that term.
          </PdpKeyTerms>
        }
      >
        Term-by-term enrollment outcomes for the entering cohort: retained, transferred out or stopped out.
      </ViewIntro>
      {/* The numbers depend on the cohort bar, which is in the URL; the intro above renders without it. */}
      <Suspense fallback={<PathsLoading />}>
        <StudentPaths />
      </Suspense>
    </>
  );
}
