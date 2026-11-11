import { routes } from "@/lib/routes";

/** The header's words. */
export const explorerHeader = {
  title: "Student Persistence and Pathway Explorer",
  source: "Source: PDP Analysis-Ready files",
  // The design's mockup said "illustrative values"; the numbers now come from the synthetic sample data.
  sampleBadge: "Synthetic sample data",
  disclaimer: "Synthetic sample data. Nothing here describes real students or institutions.",
};

/** One tab: a page under the Explorer shell. */
export type ExplorerTab = { label: string; href: string };

// Tab order, left to right. A new tab is a page folder under (uncf-explorer)/uncf/ plus a line here.
export const explorerTabs: ExplorerTab[] = [
  { label: "Student paths", href: routes.uncfPaths },
  { label: "DFW", href: routes.uncfDfw },
  { label: "Gateway courses", href: routes.uncfGateway },
  { label: "Credit momentum", href: routes.uncfCreditMomentum },
  { label: "Chat", href: routes.uncfChat },
];

/** One value a filter can take. */
export type FilterOption = { value: string; label: string };

/** One cohort filter: its URL key, its label, and the values it offers. */
export type CohortFilterDefinition = {
  id: string;
  label: string;
  options: FilterOption[];
  /** The value when the URL doesn't set one. Without it, the filter starts at "All". */
  defaultValue?: string;
  /** Always has a value (the cohort year), so it offers no "All". */
  required?: boolean;
  /** The tabs (their href) that show this filter. Without it, every tab does. */
  tabs?: string[];
  /** Show a search box above a long list. */
  searchable?: boolean;
  /** A note under the list. Without it, the list says small groups are hidden. */
  hint?: string;
};

const UNKNOWN: FilterOption = { value: "UNKNOWN", label: "Unknown" };

// The cohort bar, left to right. Each id is the URL key and the API's query name, and each value is the measures'
// own (measures/models.py), so a page passes the filters to its endpoint as they are. Labels follow the design.
export const cohortFilters: CohortFilterDefinition[] = [
  {
    id: "cohort",
    label: "Cohort",
    defaultValue: "2023-24",
    required: true,
    hint: "Students who entered each year.",
    options: ["2021-22", "2022-23", "2023-24", "2024-25"].map((year) => ({ value: year, label: year })),
  },
  {
    id: "cohort_term",
    label: "Starting term",
    options: [
      { value: "Fall", label: "Fall" },
      { value: "Winter", label: "Winter" },
      { value: "Spring", label: "Spring" },
      { value: "Summer", label: "Summer" },
      UNKNOWN,
    ],
  },
  {
    id: "enrollment_intensity",
    label: "Full / part-time",
    options: [{ value: "Full-time", label: "Full-time" }, { value: "Part-time", label: "Part-time" }, UNKNOWN],
  },
  {
    id: "enrollment_type",
    label: "Enrollment type",
    options: [
      { value: "First-time", label: "First-time" },
      { value: "Transfer-in", label: "Transfer-in" },
      { value: "Re-admit", label: "Re-admit" },
      UNKNOWN,
    ],
  },
  {
    id: "pell",
    label: "Pell (year 1)",
    options: [{ value: "Y", label: "Pell recipient" }, { value: "N", label: "No Pell" }, UNKNOWN],
  },
  {
    id: "gender",
    label: "Gender",
    options: [
      { value: "F", label: "Female" },
      { value: "M", label: "Male" },
      { value: "X", label: "Nonbinary, intersex, and gender-nonconforming" },
      { value: "P", label: "Prefer not to specify" },
      UNKNOWN,
    ],
  },
  {
    id: "race",
    label: "Race",
    searchable: true,
    options: [
      "American Indian or Alaska Native",
      "Asian",
      "Black or African American",
      "Hispanic",
      "Native Hawaiian or Other Pacific Islander",
      "Nonresident alien",
      "Two or More Races",
      "White",
    ]
      .map((race) => ({ value: race, label: race }))
      .concat(UNKNOWN),
  },
  {
    id: "ethnicity",
    label: "Ethnicity",
    // The cohort file's codes (data/dictionaries/arf_cohort_data_dictionary.md).
    options: [{ value: "H", label: "Hispanic" }, { value: "N", label: "Not Hispanic" }, UNKNOWN],
  },
  {
    id: "age_band",
    label: "Age at entry",
    options: [
      { value: "20 and younger", label: "20 and younger" },
      { value: "> 20-24", label: "Over 20 to 24" },
      { value: "Older than 24", label: "Older than 24" },
      UNKNOWN,
    ],
  },
  {
    // Which retention measure the tabs that report retention use (the API's retention_type). Their words come from
    // the shared definitions: retention ("Returned here") and federal_retention ("Back next fall").
    id: "retention_type",
    label: "Retention",
    defaultValue: "school",
    required: true,
    tabs: [routes.uncfGateway, routes.uncfCreditMomentum],
    hint: "Returned here: the PDP retention flag (enrolled here in the next academic year, or a credential). Back next fall: took a course here the fall after year 1.",
    options: [
      { value: "school", label: "Returned here" },
      { value: "federal", label: "Back next fall" },
    ],
  },
];

// A tab's own starting values, where they differ from the bar's. The design's Student paths follows first-time students.
export const tabFilterDefaults: Record<string, Record<string, string>> = {
  [routes.uncfPaths]: { enrollment_type: "First-time" },
};
