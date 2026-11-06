type UploadStatusLineProps = {
  /** A caller-formatted date, such as "today" or "Oct 28". */
  lastUpload: string;
  warningCount: number | null;
};

/** Reports the last saved upload and the number of rows flagged by its checks. */
export function UploadStatusLine({ lastUpload, warningCount }: UploadStatusLineProps) {
  const checks = warningCount === null
    ? "check results unavailable"
    : warningCount === 0
    ? "all files passed checks"
    : `${warningCount.toLocaleString("en-US")} ${warningCount === 1 ? "warning" : "warnings"} from the checks`;
  return (
    <p>
      Last upload {lastUpload} · {checks}
    </p>
  );
}
