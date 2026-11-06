import type { GuideField } from "@/components/workbench/shared/dictionary-types";

/** Small synthetic dictionary examples, not profiles measured from student files. */
export const guideFields: GuideField[] = [
  {
    id: "cohort.pell", title: "Pell grant", group: "Cohort", file: "cohort.csv",
    description: "**Federal aid** for students with high financial need. `Y` means yes.", source: "Synthetic dictionary example",
    values: [{ code: "Y", meaning: "Yes" }, { code: "N", meaning: "No" }],
    profile: { totalRows: 100, fillPercent: 80, distinctCount: 2, topValues: [{ value: "Y", count: 50 }, { value: "N", count: 30 }] },
  },
  { id: "course.gateway", title: "Gateway math", group: "Course", file: "course.csv", description: "The first college-level math course a program requires.", source: "Synthetic dictionary example" },
  { id: "aid.fafsa", title: "FAFSA application", group: "Financial aid", file: "financial-aid.csv", description: "A documented field absent from these example files.", source: "Synthetic dictionary example", notInData: true },
];

export const guideGroups = ["All", "Cohort", "Course", "Financial aid"].map((label) => ({ id: label, label }));
export const guideSections = guideGroups.filter((group) => group.id !== "All").map((group) => ({
  ...group,
  fields: guideFields.filter((field) => field.group === group.id).map((field) => ({ id: field.id, title: field.title, notInData: field.notInData })),
}));
