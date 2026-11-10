import type { Metadata } from "next";
import { Suspense } from "react";

import { ViewIntro } from "@/components/uncf/layout/view-intro";
import { PathsLoading, StudentPaths } from "@/components/uncf/paths/student-paths";

export const metadata: Metadata = { title: "Student paths" };

/** The Student paths tab: where the entering cohort is, term by term. */
export default function StudentPathsPage() {
  return (
    <>
      <ViewIntro
        title="Student Paths"
        whatThisShows="Every first-time student in the selected entering cohort, followed through their next two fall or spring terms."
        howToRead="Band width = number of students. Bands split where students leave or transfer, and rejoin when they return."
        keyTerms="Retention: enrolled at this institution. Persistence: enrolled anywhere. Stopped out: not enrolled anywhere."
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
