import type { CheckResult } from "@/components/workbench/upload/check-results-list";
import type { SavedTable } from "@/components/workbench/upload/upload-saved-callout";
import type { UploadedFile } from "@/components/workbench/upload/uploaded-file-list";

// Synthetic examples shaped like a check of the mock AR files; they are not measured results.

export const uploadStepLabels = ["Choose files", "Check", "Save"];

export const mockUploadedFiles: UploadedFile[] = [
  { id: "upload-cohort", name: "pdp_cohort_data.csv", kind: "Cohort", status: "checked", rowCount: 10313, columnCount: 85 },
  { id: "upload-course", name: "pdp_course_data.csv", kind: "Course", status: "checked", rowCount: 100951, columnCount: 35 },
];

export const financialAidNote = "Financial aid files can't be loaded yet. Their fields are listed in the field guide.";

export const mockCheckResults: CheckResult[] = [
  { id: "cohort-file", severity: "ok", title: "Recognized as a cohort file", detail: "85 columns, 10,313 students, cohorts 2021-22 to 2024-25." },
  { id: "course-file", severity: "ok", title: "Recognized as a course file", detail: "35 columns, 100,951 course records. Linked to students on Student ID + Cohort." },
  { id: "two-cohorts", severity: "warning", title: "2 students appear in two cohorts", detail: "They are kept as separate records. Join on Student ID + Cohort, not Student ID alone.", fieldId: "Student_GUID" },
  { id: "pell-code", severity: "warning", title: "Pell status uses a code the dictionary doesn't list", detail: "759 students have “U”. They'll be shown as Unknown.", fieldId: "Pell_Status_First_Year" },
  { id: "working", severity: "warning", title: "Working status is almost always unknown", detail: "10,302 of 10,313 students have -1 or 0 (unknown).", fieldId: "EmploymentStatus" },
  { id: "enrollment-type", severity: "info", title: "2 students have Enrollment Type “Continuing”", detail: "Not in the dictionary's list. Kept as-is.", fieldId: "Enrollment_Type" },
];

export const blockingCheckResults: CheckResult[] = [
  { id: "cohort-file", severity: "ok", title: "Recognized as a cohort file", detail: "85 columns, 10,313 students, cohorts 2021-22 to 2024-25." },
  { id: "same-name", severity: "error", title: "Both files are named data.csv", detail: "Rename one of them and add them again. Each file's report is named after the file." },
];

export const mockSavedTables: SavedTable[] = [
  { name: "cohort", rowCount: 10313 },
  { name: "course", rowCount: 100951 },
];
