"use client";

import type { ComponentProps } from "react";
import { CircleX } from "lucide-react";
import { PageIntro } from "@/components/page-intro";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CheckResultsList } from "@/components/workbench/upload/check-results-list";
import { FileDropzone } from "@/components/workbench/upload/file-dropzone";
import { UploadSavedCallout } from "@/components/workbench/upload/upload-saved-callout";
import { UploadSteps } from "@/components/workbench/upload/upload-steps";
import { UploadedFileList } from "@/components/workbench/upload/uploaded-file-list";

export type UploadStage = "choose" | "checking" | "checked" | "saved";
export type UploadPageProps = {
  stage: UploadStage;
  error?: string;
  steps: ComponentProps<typeof UploadSteps>;
  dropzone: Omit<ComponentProps<typeof FileDropzone>, "onRejectedFiles">;
  /** Lets the route explain why a picked or dropped file was refused. */
  onRejectedFiles?: ComponentProps<typeof FileDropzone>["onRejectedFiles"];
  files: ComponentProps<typeof UploadedFileList>;
  checks: ComponentProps<typeof CheckResultsList>;
  saved: ComponentProps<typeof UploadSavedCallout>;
};

/** Presents an upload stage while the caller owns checking, saving and navigation. */
export function UploadPage({ stage, error, steps, dropzone, onRejectedFiles, files, checks, saved }: UploadPageProps) {
  return (
    <div className="flex max-w-3xl flex-col gap-6">
      <PageIntro size="sm" title="Upload AR files">
        <p>Choose cohort and course CSV files, check them, then save them to the configured database.</p>
      </PageIntro>
      <UploadSteps {...steps} />
      {error && (
        <Alert variant="destructive">
          <CircleX aria-hidden />
          <AlertTitle>That didn&apos;t go through</AlertTitle>
          <AlertDescription>
            <p>{error}</p>
          </AlertDescription>
        </Alert>
      )}
      {stage === "choose" && <FileDropzone {...dropzone} onRejectedFiles={onRejectedFiles} />}
      {stage !== "choose" && <UploadedFileList {...files} />}
      {stage === "checked" && <CheckResultsList {...checks} />}
      {stage === "saved" && <UploadSavedCallout {...saved} />}
    </div>
  );
}
