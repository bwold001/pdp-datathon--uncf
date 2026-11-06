"use client";

import Link from "next/link";
import type { ComponentProps } from "react";
import { PageIntro } from "@/components/page-intro";
import { Button, buttonVariants } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { NumberedStepCard } from "@/components/workbench/home/numbered-step-card";
import { homeSteps } from "@/content/workbench";

type HomeFirstRunProps = {
  uploadHref: string;
  fieldGuideHref: string;
  onUseMockData: () => void;
  loadingMockData?: boolean;
  children?: React.ReactNode;
};

/** Introduces the workbench and offers an upload or synthetic mock-data load. */
export function HomeFirstRun({ uploadHref, fieldGuideHref, onUseMockData, loadingMockData = false, children }: HomeFirstRunProps) {
  const intro: ComponentProps<typeof PageIntro> = {
    size: "sm", eyebrow: "No data yet", title: "Start with your AR files",
    children: <p>Upload your cohort and course CSV files. They are checked against the data dictionary and saved to the configured database.</p>,
  };
  return (
    <div className="flex max-w-3xl flex-col gap-6">
      <PageIntro {...intro} />
      <ol className="grid gap-3 sm:grid-cols-3">
        {homeSteps.map((step, index) => (
          <li key={step.title}>
            <NumberedStepCard step={index + 1} title={step.title}>
              {step.text}
            </NumberedStepCard>
          </li>
        ))}
      </ol>
      <div className="flex flex-wrap gap-2">
        <Link href={uploadHref} className={buttonVariants({ size: "lg" })}>
          Upload AR files
        </Link>
        <Button variant="outline" size="lg" onClick={onUseMockData} disabled={loadingMockData}>
          {loadingMockData && <Spinner aria-hidden />}
          Try it with the mock data
        </Button>
      </div>
      <p className="text-sm text-muted-foreground">
        You can browse the{" "}
        <Link href={fieldGuideHref} className="underline underline-offset-4 hover:text-foreground">
          field guide
        </Link>{" "}
        without uploading anything.
      </p>
      {children}
    </div>
  );
}
