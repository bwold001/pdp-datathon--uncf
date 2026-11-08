import type { Metadata } from "next";
import { Suspense } from "react";

import { PageIntro } from "@/components/page-intro";
import { Skeleton } from "@/components/ui/skeleton";

import { CardFromAddress } from "./card-from-address";

export const metadata: Metadata = {
  title: "Make an insight card",
  description: "A one-page card from an Explorer view, with its definition, limits and source, ready to print or save as PDF.",
};

/** The insight card maker (#8). The address names the view: ?cohort=2022-23&group_by=pell&measure=retention. */
export default function CardPage({ searchParams }: PageProps<"/uncf/card">) {
  return (
    <>
      <PageIntro eyebrow="UNCF · Insight card" title="Make an insight card" size="sm">
        <p>
          One page that carries its own definition, limits and source, so nobody has to ask what the number means. Synthetic
          sample data, not real students.
        </p>
      </PageIntro>
      <Suspense fallback={<Skeleton className="h-96 rounded-2xl" />}>
        <CardFromAddress searchParams={searchParams} />
      </Suspense>
    </>
  );
}
