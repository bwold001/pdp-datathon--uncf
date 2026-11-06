"use client";

import { useState } from "react";

import { useContextPanel } from "@/components/workbench/context-panel/context-panel-provider";
import { UploadPage, type UploadStage } from "@/components/workbench/upload/upload-page";
import type { CheckResult } from "@/components/workbench/upload/check-results-list";
import type { SavedTable } from "@/components/workbench/upload/upload-saved-callout";
import { createUploadedFile, type UploadedFile } from "@/components/workbench/upload/uploaded-file-list";
import { financialAidNote, uploadSteps } from "@/content/workbench";
import { describeError } from "@/lib/errors";
import { routes } from "@/lib/routes";
import {
  detectKind,
  KIND_LABELS,
  progressNote,
  readHeader,
  savedTablesFromSummary,
  summaryLines,
  uploadErrorResult,
  uploadResults,
} from "@/services/workbench-mappers";
import { createUpload, type ColumnDefinition, type RunRequest, type RunStatus, type SourceKind, type Upload } from "@/services/workbench";
import { useWorkbenchData } from "@/app/(dashboard)/workbench/workbench-data";

type Saved = { tables: SavedTable[]; lines: string[]; note: string };

/** One chosen file after checking: its row, its findings, and the stored upload if it was accepted. */
type CheckedFile = { row: UploadedFile; results: CheckResult[]; upload?: Upload };

const MOCK_FILES: UploadedFile[] = [
  { id: "mock-cohort", name: "pdp_cohort_data.csv (mock)", kind: "Cohort", status: "checking" },
  { id: "mock-course", name: "pdp_course_data.csv (mock)", kind: "Course", status: "checking" },
];

/** A chosen file with its header read: the kind it was recognized as, or why it can't be used. */
type ClassifiedFile = { file: File; row: UploadedFile; columnCount: number } & ({ kind: SourceKind } | { problem: string });

/** Read each header and work out its kind. One file of each kind at most, so a second one is refused. */
async function classifyFiles(chosen: File[], columns: ColumnDefinition[], entries: UploadedFile[]): Promise<ClassifiedFile[]> {
  const headers = await Promise.all(chosen.map(readHeader));
  const kindsTaken = new Set<SourceKind>();
  return chosen.map((file, index) => {
    const columnCount = headers[index].length;
    const kind = detectKind(headers[index], columns, file.name);
    const row: UploadedFile = { ...entries[index], kind: kind ? KIND_LABELS[kind] : "Unknown", status: "checked", columnCount };
    if (kind === null) {
      return { file, row, columnCount, problem: "It can't be told apart as a cohort or a course file from its columns. Put \"cohort\" or \"course\" in its name and add it again." };
    }
    if (kindsTaken.has(kind)) {
      return { file, row, columnCount, problem: `Another ${kind} file was added too. Add one of each at most.` };
    }
    kindsTaken.add(kind);
    return { file, row, columnCount, kind };
  });
}

/** Store a recognized file on the server, which checks its header against the mapping config. */
async function checkFile(classified: ClassifiedFile): Promise<CheckedFile> {
  const { file, row, columnCount } = classified;
  if ("problem" in classified) return { row, results: [uploadErrorResult(file.name, classified.problem)] };
  try {
    const upload = await createUpload(classified.kind, file);
    return { row, results: uploadResults(upload, columnCount), upload };
  } catch (error) {
    return { row, results: [uploadErrorResult(file.name, describeError(error))] };
  }
}

/** For a kind with no upload, say that the run loads the mock file in its place. */
function missingKindResults(uploads: Upload[]): CheckResult[] {
  return (["cohort", "course"] as const)
    .filter((kind) => !uploads.some((upload) => upload.kind === kind))
    .map((kind) => ({
      id: `missing-${kind}`,
      severity: "info",
      title: `No ${kind} file added`,
      detail: `The mock ${kind} file will be loaded with yours, because the data model needs both.`,
    }));
}

/** The Upload page's state: check the chosen files, then load them, and show how the load went. */
export function UploadFlow() {
  const { columns, run } = useWorkbenchData();
  const { openField } = useContextPanel();
  const [stage, setStage] = useState<UploadStage>("choose");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [results, setResults] = useState<CheckResult[]>([]);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [saved, setSaved] = useState<Saved>({ tables: [], lines: [], note: "" });
  const [error, setError] = useState<string>();

  /** Run the load; on success show the Saved step, otherwise go back to `fallback` with the reason. */
  async function load(request: RunRequest, fallback: UploadStage) {
    setError(undefined);
    const outcome = await run.start(request);
    if (outcome.status === "succeeded") {
      showSaved(outcome.run);
    } else if (outcome.status === "failed") {
      setError(outcome.message);
      setStage(fallback);
    }
  }

  /** Show the committed tables and final loader summary. */
  function showSaved(finished: RunStatus) {
    setSaved({ tables: savedTablesFromSummary(finished.summary), lines: summaryLines(finished.summary), note: finished.note });
    setFiles((current) => current.map((file) => ({ ...file, status: "saved" })));
    setStage("saved");
  }

  /** Check chosen files, preserving their upload-entry IDs through each stage. */
  async function handleFiles(chosen: File[]) {
    if (columns.status !== "success") {
      setError("The data dictionary hasn't loaded, so the files can't be recognized. Reload the page and try again.");
      return;
    }
    setError(undefined);
    setStage("checking");
    const entries = chosen.map((file) => createUploadedFile(file, "…"));
    setFiles(entries);
    let checked: CheckedFile[];
    try {
      checked = await Promise.all((await classifyFiles(chosen, columns.data, entries)).map(checkFile));
    } catch (error) {
      setError(describeError(error));
      setStage("choose");
      return;
    }
    const accepted = checked.flatMap((file) => (file.upload ? [file.upload] : []));
    setFiles(checked.map((file) => file.row));
    setUploads(accepted);
    setResults([...checked.flatMap((file) => file.results), ...(accepted.length > 0 ? missingKindResults(accepted) : [])]);
    setStage("checked");
  }

  /** Save only the checked uploads, adding the missing mock kind when needed. */
  function handleSave() {
    if (uploads.length === 0 || run.state.status === "running") return;
    const cohort = uploads.find((upload) => upload.kind === "cohort");
    const course = uploads.find((upload) => upload.kind === "course");
    void load({ cohort_upload_id: cohort?.upload_id, course_upload_id: course?.upload_id }, "checked");
  }

  /** Load the two configured synthetic source files. */
  function handleUseMockFiles() {
    setFiles(MOCK_FILES);
    setResults([]);
    setUploads([]);
    setStage("checking");
    void load({}, "choose");
  }

  /** Clear this attempt and cancel its polling. */
  function handleStartOver() {
    run.reset();
    setStage("choose");
    setFiles([]);
    setResults([]);
    setUploads([]);
    setError(undefined);
  }

  return (
    <UploadPage
      stage={stage}
      steps={{ steps: uploadSteps, currentStep: stage === "choose" ? 0 : stage === "saved" ? uploadSteps.length : 1 }}
      files={{ files, note: run.state.status === "running" ? progressNote(run.state.run?.progress ?? []) : financialAidNote }}
      dropzone={{ onFiles: handleFiles, onUseMockFiles: handleUseMockFiles, disabled: run.state.status === "running" }}
      onRejectedFiles={(rejected) => setError(`${rejected.map((file) => file.name).join(", ")}: choose CSV files only.`)}
      checks={{ results, onFieldClick: openField, onSave: handleSave, onStartOver: handleStartOver, saving: run.state.status === "running" }}
      saved={{ tables: saved.tables, children: <SavedDetails lines={saved.lines} note={saved.note} />, exploreHref: routes.workbenchExplore }}
      error={error}
    />
  );
}

/** What the load read, fixed and held back, and the synthetic-data note. */
function SavedDetails({ lines, note }: { lines: string[]; note: string }) {
  return (
    <>
      {lines.length > 0 && (
        <ul className="list-disc pl-5">
          {lines.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      {note && <p className="text-xs">{note}</p>}
    </>
  );
}
