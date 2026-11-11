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
export type FilterOption = {
  value: string;
  label: string;
  /** The words on its chip once picked, when the label alone isn't clear ("Started in Fall", "Pell unknown"). */
  chip?: string;
  /** Its word in the cohort sentence, for a filter that lives there ("first-time"). */
  word?: string;
};

/**
 * Where a filter lives in the bar: in the sentence that says who's shown, behind "Add filter", or as a setting beside
 * it (how a measure is counted, not which students).
 */
export type FilterPlace = "sentence" | "menu" | "setting";

/** The groups "Add filter" lists its filters in, in order. */
export const filterGroups = ["Enrollment", "Financial aid", "Demographics"] as const;

/** One cohort filter: its URL key, its label, and the values it offers. */
export type CohortFilterDefinition = {
  id: string;
  label: string;
  options: FilterOption[];
  place: FilterPlace;
  /** The group it's listed under in "Add filter". */
  group?: (typeof filterGroups)[number];
  /** The value when the URL doesn't set one. Without it, the filter starts at "All". */
  defaultValue?: string;
  /** Always has a value (the cohort year), so it offers no "All". */
  required?: boolean;
  /** The tabs (their href) that show this filter. Without it, every tab does. */
  tabs?: string[];
  /** Its words in the sentence when it's "All" ("of every enrollment type"). */
  allWord?: string;
  /** Its "All" row in a list, when not "Any" ("Every enrollment type"). */
  allLabel?: string;
  /** A note under its list. */
  hint?: string;
};

/** "Unknown", with a chip that says which field is unknown, and its words when it's in the sentence. */
const unknown = (field: string, word?: string): FilterOption => ({ value: "UNKNOWN", label: "Unknown", chip: `${field} unknown`, word });

// The cohort bar's filters. Each id is the URL key and the API's query name, and each value is the measures' own
// (measures/models.py), so a page passes the filters to its endpoint as they are. The class year and enrollment type
// are in the sentence that says who's shown; the rest are behind "Add filter", in its groups' order.
export const cohortFilters: CohortFilterDefinition[] = [
  {
    id: "cohort",
    label: "Entering class",
    place: "sentence",
    defaultValue: "2023-24",
    required: true,
    options: ["2021-22", "2022-23", "2023-24", "2024-25"].map((year) => ({ value: year, label: year, word: year })),
  },
  {
    id: "enrollment_type",
    label: "Enrollment type",
    place: "sentence",
    allWord: "of every enrollment type",
    allLabel: "Every enrollment type",
    options: [
      { value: "First-time", label: "First-time", word: "first-time" },
      { value: "Transfer-in", label: "Transfer-in", word: "transfer-in" },
      { value: "Re-admit", label: "Re-admitted", word: "re-admitted" },
      unknown("Enrollment type", "of unknown enrollment type"),
    ],
  },
  {
    id: "cohort_term",
    label: "Starting term",
    place: "menu",
    group: "Enrollment",
    options: [
      { value: "Fall", label: "Fall", chip: "Started in Fall" },
      { value: "Winter", label: "Winter", chip: "Started in Winter" },
      { value: "Spring", label: "Spring", chip: "Started in Spring" },
      { value: "Summer", label: "Summer", chip: "Started in Summer" },
      unknown("Starting term"),
    ],
  },
  {
    id: "enrollment_intensity",
    label: "Full / part-time",
    place: "menu",
    group: "Enrollment",
    options: [{ value: "Full-time", label: "Full-time" }, { value: "Part-time", label: "Part-time" }, unknown("Full / part-time")],
  },
  {
    id: "pell",
    label: "Pell (year 1)",
    place: "menu",
    group: "Financial aid",
    options: [{ value: "Y", label: "Pell recipient" }, { value: "N", label: "No Pell" }, unknown("Pell")],
  },
  {
    id: "gender",
    label: "Gender",
    place: "menu",
    group: "Demographics",
    options: [
      { value: "F", label: "Female" },
      { value: "M", label: "Male" },
      { value: "X", label: "Nonbinary, intersex, and gender-nonconforming", chip: "Nonbinary" },
      { value: "P", label: "Prefer not to specify", chip: "Gender not specified" },
      unknown("Gender"),
    ],
  },
  {
    id: "race",
    label: "Race",
    place: "menu",
    group: "Demographics",
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
      // Race has its own "Hispanic", apart from the Ethnicity filter's, so its chip says which.
      .map((race): FilterOption => ({ value: race, label: race, chip: race === "Hispanic" ? "Hispanic (race)" : race }))
      .concat(unknown("Race")),
  },
  {
    id: "ethnicity",
    label: "Ethnicity",
    place: "menu",
    group: "Demographics",
    // The cohort file's codes (data/dictionaries/arf_cohort_data_dictionary.md).
    options: [{ value: "H", label: "Hispanic" }, { value: "N", label: "Not Hispanic" }, unknown("Ethnicity")],
  },
  {
    id: "age_band",
    label: "Age at entry",
    place: "menu",
    group: "Demographics",
    options: [
      { value: "20 and younger", label: "20 and younger", chip: "Age 20 and younger" },
      { value: "> 20-24", label: "Over 20 to 24", chip: "Age over 20 to 24" },
      { value: "Older than 24", label: "Older than 24", chip: "Age older than 24" },
      unknown("Age"),
    ],
  },
  {
    // Which retention measure the tabs that report retention use (the API's retention_type). Their words come from
    // the shared definitions: retention ("Returned here") and federal_retention ("Back next fall").
    id: "retention_type",
    label: "Retention",
    place: "setting",
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
