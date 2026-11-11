/**
 * Words for groups too small to show. The API leaves out the numbers of any group with fewer than `min_students`
 * students (in every answer's meta and in the cohort options). The server sets it with UNCF_MIN_STUDENTS: 1, the
 * default for this synthetic data, shows every group with students; 10 hides small groups to protect privacy.
 */

/** Whether the API hides small groups at all: only when its minimum is above 1. */
export function hidesSmallGroups(minStudents: number): boolean {
  return minStudents > 1;
}

/** How a count with no number reads: "Under 10" when small groups are hidden, otherwise "None". */
export function hiddenCount(minStudents: number): string {
  return hidesSmallGroups(minStudents) ? `Under ${minStudents}` : "None";
}

/** The start of a "too few" message, e.g. "Fewer than 10 students" or "No students". */
export function tooFew(minStudents: number, students = "students"): string {
  return hidesSmallGroups(minStudents) ? `Fewer than ${minStudents} ${students}` : `No ${students}`;
}

/** "Groups under 10 students are hidden to protect privacy.", or "" when nothing is hidden. */
export function privacyNote(minStudents: number): string {
  return hidesSmallGroups(minStudents) ? `Groups under ${minStudents} students are hidden to protect privacy.` : "";
}
