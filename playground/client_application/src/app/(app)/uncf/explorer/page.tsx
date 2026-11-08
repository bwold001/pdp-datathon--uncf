import type { Metadata } from "next";

import { PageIntro } from "@/components/page-intro";
import { Explorer } from "@/components/uncf/explorer/explorer";

export const metadata: Metadata = {
  title: "Student Success Explorer",
  description: "Outcomes by student group for each entering class, with the definition beside every chart.",
};

/** The UNCF Student Success Explorer page (#6). */
export default function ExplorerPage() {
  return (
    <>
      <PageIntro eyebrow="UNCF · Student Success Explorer" title="How are students doing, and for which groups?" size="sm">
        <p>
          Pick an entering class and up to two ways to group students. Each chart has its definition beside it, and a
          hidden or missing number is labeled, never shown as 0. Synthetic sample data, not real students.
        </p>
      </PageIntro>
      <Explorer />
    </>
  );
}
