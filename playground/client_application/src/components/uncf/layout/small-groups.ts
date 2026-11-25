/** Aggregate visibility never depends on a minimum group size. */

/** Historical minimum settings cannot restore numerical hiding. */
export function hidesSmallGroups(_minStudents: number): boolean {
  void _minStudents;
  return false;
}

/** An absent count is not a hidden small count. */
export function hiddenCount(_minStudents: number): string {
  void _minStudents;
  return "Unavailable";
}

/** Explain missing population evidence without implying a privacy threshold. */
export function tooFew(_minStudents: number, students = "students"): string {
  void _minStudents;
  return `No reported ${students}`;
}

/** No size-based privacy guarantee is made for visible synthetic aggregates. */
export function privacyNote(_minStudents: number): string {
  void _minStudents;
  return "";
}
