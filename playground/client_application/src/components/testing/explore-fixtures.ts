// Synthetic student rows for Explore page stories. Generated from fixed rules, so every story run sees the
// same rows; they are not measured PDP results.

export type ExploreRow = {
  id: string;
  Program_of_Study_Year_1: string;
  Cohort: string;
  Pell_Status_First_Year: "Yes" | "No";
  Gateway_Math_Status: "Passed" | "Not passed";
  CompletedGatewayEnglishYear1: "Completed Y1" | "Did not complete" | "Not reported";
  Math_or_English_Gateway: string;
  EmploymentStatus: string;
  Gender: string;
  Race: string;
  Enrollment_Intensity_First_Term: string;
  First_Gen: string;
  Credits_Earned_Year_1: number;
  Retention: "Retained" | "Not retained";
};

const programs = ["Health professions", "Business", "Liberal arts", "Engineering technology"];
const cohorts = ["2021-22", "2022-23", "2023-24", "2024-25"];

export const exploreRows: ExploreRow[] = Array.from({ length: 48 }, (_, index) => ({
  id: `S${String(index + 1).padStart(4, "0")}`,
  Program_of_Study_Year_1: programs[index % programs.length],
  Cohort: cohorts[Math.floor(index / 12)],
  Pell_Status_First_Year: index % 3 === 0 ? "No" : "Yes",
  Gateway_Math_Status: index % 5 < 3 ? "Passed" : "Not passed",
  CompletedGatewayEnglishYear1: index % 7 === 0 ? "Not reported" : index % 3 === 0 ? "Did not complete" : "Completed Y1",
  Math_or_English_Gateway: ["Math + English", "Math only", "English only", "None"][index % 4],
  EmploymentStatus: ["Working", "Not working", "Unknown"][index % 3],
  Gender: ["Female", "Male", "Not reported"][index % 3],
  Race: ["Black or African American", "Asian", "Hispanic", "White"][index % 4],
  Enrollment_Intensity_First_Term: index % 2 ? "Part-time" : "Full-time",
  First_Gen: ["Yes", "No", "Not reported"][index % 3],
  Credits_Earned_Year_1: (index * 7) % 42,
  Retention: index % 4 === 3 ? "Not retained" : "Retained",
}));

/** The filters the Explore page story offers, keyed by the field each one filters on. */
export const exploreFilters = [
  { fieldId: "Program_of_Study_Year_1", label: "Program", question: "What program is the student in?", values: programs },
  { fieldId: "Math_or_English_Gateway", label: "Gateway courses", question: "Which gateway courses did they take?", values: ["Math + English", "Math only", "English only", "None"] },
  { fieldId: "Gateway_Math_Status", label: "Gateway math Y1", question: "Did they pass gateway math in year 1?", values: ["Passed", "Not passed"] },
  { fieldId: "CompletedGatewayEnglishYear1", label: "Gateway English Y1", question: "Did they pass gateway English in year 1?", values: ["Completed Y1", "Did not complete", "Not reported"] },
  { fieldId: "EmploymentStatus", label: "Working", question: "Is the student working?", values: ["Working", "Not working", "Unknown"] },
  { fieldId: "Gender", label: "Gender", question: "Gender", values: ["Female", "Male", "Not reported"] },
  { fieldId: "Race", label: "Race", question: "Race", values: ["Black or African American", "Asian", "Hispanic", "White"] },
  { fieldId: "Pell_Status_First_Year", label: "Pell", question: "Did they receive a Pell grant in year 1?", values: ["Yes", "No"] },
  { fieldId: "Cohort", label: "Cohort", question: "Which year did they start?", values: cohorts },
  { fieldId: "Enrollment_Intensity_First_Term", label: "Full/part-time", question: "Full-time or part-time in their first term?", values: ["Full-time", "Part-time"] },
  { fieldId: "First_Gen", label: "First-gen", question: "First in their family to go to college?", values: ["Yes", "No", "Not reported"] },
] as const satisfies { fieldId: keyof ExploreRow; label: string; question: string; values: readonly string[] }[];
