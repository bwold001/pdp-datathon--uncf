import { Badge } from "@/components/ui/badge";
import { Item, ItemActions, ItemContent, ItemDescription, ItemMedia, ItemTitle } from "@/components/ui/item";
import { Spinner } from "@/components/ui/spinner";

export type UploadedFileStatus = "checking" | "checked" | "saved";

export type UploadedFile = {
  /** Unique upload-entry identity, kept through checking and saving, even if the name changes. */
  id: string;
  name: string;
  /** What the file holds, such as "Cohort" or "Course". */
  kind: string;
  status: UploadedFileStatus;
  /** Unknown until the file has been read. */
  rowCount?: number;
  columnCount?: number;
};

/** Call once when accepting a file; a replacement or repeat selection gets a new upload-entry ID. */
export function createUploadedFile(file: File, kind: string): UploadedFile {
  return { id: crypto.randomUUID(), name: file.name, kind, status: "checking" };
}

const statusText: Record<UploadedFileStatus, string> = {
  checking: "Checking…",
  checked: "Checked",
  saved: "Saved",
};

/** "10,313 rows · 85 columns", or nothing while the counts are unknown. */
function sizeText({ rowCount, columnCount }: UploadedFile) {
  const parts = [];
  if (rowCount !== undefined) parts.push(`${rowCount.toLocaleString("en-US")} rows`);
  if (columnCount !== undefined) parts.push(`${columnCount.toLocaleString("en-US")} columns`);
  return parts.join(" · ");
}

/** One uploaded file: its name and size, what kind of file it is, and how far it has got. */
export function UploadedFileRow({ file }: { file: UploadedFile }) {
  const size = sizeText(file);
  return (
    <Item variant="outline" data-status={file.status}>
      <ItemMedia className="size-9 rounded-full bg-muted text-xs font-medium" aria-hidden>
        CSV
      </ItemMedia>
      <ItemContent>
        <ItemTitle className="break-all">{file.name}</ItemTitle>
        {size && <ItemDescription className="tabular-nums">{size}</ItemDescription>}
      </ItemContent>
      <ItemActions>
        <Badge variant="outline">{file.kind}</Badge>
        <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
          {file.status === "checking" && <Spinner aria-hidden />}
          {statusText[file.status]}
        </span>
      </ItemActions>
    </Item>
  );
}

type UploadedFileListProps = {
  files: UploadedFile[];
  /** A line under the list, such as which kinds of file weren't added. */
  note?: React.ReactNode;
};

/** The files being uploaded, one row each, with an optional note underneath. */
export function UploadedFileList({ files, note }: UploadedFileListProps) {
  return (
    <div className="flex flex-col gap-2">
      <ul aria-label="Uploaded files" className="flex flex-col gap-2">
        {files.map((file) => (
          <li key={file.id}>
            <UploadedFileRow file={file} />
          </li>
        ))}
      </ul>
      {note && <p className="text-sm text-muted-foreground">{note}</p>}
    </div>
  );
}
