"use client";

import { useState } from "react";
import { Upload } from "lucide-react";
import { cn } from "cn";

import { Button } from "@/components/ui/button";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/components/ui/empty";
import { FileUploadButton } from "@/components/file-upload-button";

type FileDropzoneProps = {
  /** Called with the dropped or chosen files that match `accept`. */
  onFiles: (files: File[]) => void;
  /** Called with dropped files that don't match `accept`, so the page can say why they were left out. */
  onRejectedFiles?: (files: File[]) => void;
  /** Shows a "Use the mock files" button when given. */
  onUseMockFiles?: () => void;
  /** Accepted extensions, MIME types or MIME wildcards, comma-separated as in a file input. */
  accept?: string;
  disabled?: boolean;
  description?: React.ReactNode;
};

/** Matches one normalized accept entry against the file's extension or MIME type. */
function matchesAcceptEntry(file: File, entry: string) {
  if (entry.startsWith(".")) return file.name.toLowerCase().endsWith(entry);
  if (entry.endsWith("/*")) return file.type.toLowerCase().startsWith(entry.slice(0, -1));
  return file.type.toLowerCase() === entry;
}

/** Matches file input accept entries; an empty list allows every file. */
function matchesAccept(file: File, accept: string) {
  const entries = accept.split(",").map((entry) => entry.trim().toLowerCase()).filter(Boolean);
  return entries.length === 0 || entries.some((entry) => matchesAcceptEntry(file, entry));
}

/**
 * A dashed area to drop CSV files on, with buttons to pick files or use the mock files instead. Its only
 * state is whether files are being dragged over it; what happens to the files is up to the page.
 */
export function FileDropzone({
  onFiles,
  onRejectedFiles,
  onUseMockFiles,
  accept = ".csv",
  disabled = false,
  description = "Add your cohort and course files together. They're checked, then linked on Student ID + Cohort.",
}: FileDropzoneProps) {
  const [dragging, setDragging] = useState(false);

  /** Splits dropped or picked files into the ones `accept` allows and the rest. The picker's filter is only a hint. */
  function handleFiles(files: File[]) {
    const accepted = files.filter((file) => matchesAccept(file, accept));
    const rejected = files.filter((file) => !matchesAccept(file, accept));
    if (accepted.length > 0) onFiles(accepted);
    if (rejected.length > 0) onRejectedFiles?.(rejected);
  }

  /** Stops the browser from opening the dropped files, then filters them unless the zone is disabled. */
  function handleDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    if (!disabled) handleFiles(Array.from(event.dataTransfer.files));
  }

  /** Keeps the drag-over look until the pointer leaves the zone itself, not one of its children. */
  function handleDragLeave(event: React.DragEvent<HTMLDivElement>) {
    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setDragging(false);
  }

  return (
    <Empty
      data-dragging={dragging || undefined}
      aria-disabled={disabled || undefined}
      onDragOver={(event) => {
        // Leave disabled drags uncancelled so the browser shows its can't-drop cursor.
        if (disabled) return;
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={cn("border-2 transition-colors", dragging && "border-primary bg-muted", disabled && "opacity-50")}
    >
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Upload aria-hidden />
        </EmptyMedia>
        <EmptyTitle>
          <h2>Drop CSV files here</h2>
        </EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
      <EmptyContent className="flex-row flex-wrap justify-center">
        <FileUploadButton size="lg" accept={accept} multiple disabled={disabled} onFiles={handleFiles} />
        {onUseMockFiles && (
          <Button size="lg" variant="outline" disabled={disabled} onClick={onUseMockFiles}>
            Use the mock files
          </Button>
        )}
      </EmptyContent>
    </Empty>
  );
}
