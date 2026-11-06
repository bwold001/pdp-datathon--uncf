import type { FieldDefinition, DescribedItem } from "@/components/workbench/shared/dictionary-types";

/** Deliberately small synthetic examples, not profiles measured from the PDP files. */
export const terms: DescribedItem[] = [
  { id: "Cohort", label: "Cohort", description: "Students who started in the same academic year." },
  { id: "Gateway_Math_Status", label: "Gateway course", description: "The first college-level math or English course a program requires." },
  { id: "Retention", label: "Retention", description: "Continued enrollment or completion at the starting institution." },
  { id: "Persistence", label: "Persistence", description: "Continued enrollment or completion at another institution." },
  { id: "Pell_Status_First_Year", label: "Pell grant", description: "Federal aid for students with high financial need." },
  { id: "Program_of_Study_Year_1", label: "Program area", description: "The student's program, grouped by CIP code." },
];
/** Explicit fields keep each synthetic dictionary example easy to copy. */
export const fields: FieldDefinition[] = [
  { id: "Cohort", title: "Cohort", description: "Students who started in the same academic year.", source: "cohort" },
  { id: "Gateway_Math_Status", title: "Gateway course", description: "The first college-level math or English course a program requires.", source: "cohort" },
  { id: "Retention", title: "Retention", description: "Continued enrollment or completion at the starting institution.", source: "cohort" },
  { id: "Persistence", title: "Persistence", description: "Continued enrollment or completion at another institution.", source: "cohort" },
  {
    id: "Pell_Status_First_Year", title: "Did they get a Pell grant in year 1?",
    description: "Federal aid for students with high financial need.", source: "cohort",
    values: [{ code: "Y", meaning: "Yes" }, { code: "N", meaning: "No" }],
    profile: { totalRows: 100, fillPercent: 80, distinctCount: 2, topValues: [{ value: "Y", count: 50 }, { value: "N", count: 30 }] },
  },
  { id: "Program_of_Study_Year_1", title: "Program area", description: "The student's program, grouped by CIP code.", source: "cohort" },
];
export const caveats: DescribedItem[] = [{ id: "Pell_Status_First_Year", label: "Some Pell statuses are missing", description: "This synthetic example leaves 20 of 100 rows blank." }];
export const beforeUpload = "AR files describe student cohorts and courses. Upload files to start exploring. All examples here use synthetic PDP data.";
export const afterUpload = "One row per student and cohort. This story uses 100 synthetic example rows, not measured PDP results.";
