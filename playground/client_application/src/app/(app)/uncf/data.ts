/**
 * The UNCF Results API contract (#5), mirrored by hand, and the Explorer's loader.
 *
 * Until #5 exists, `resultsLoader` reads a fixture of the saved precompute rows
 * (`python -m uncf && python -m uncf.explorer_fixture`). When #5 lands, only `loadResults` changes.
 */

export const measures = ["retention", "gateway_math", "gateway_english"] as const;
export type Measure = (typeof measures)[number];

export const cohorts = ["2021-22", "2022-23", "2023-24", "2024-25"] as const;
export type Cohort = (typeof cohorts)[number];

/** The groupings the Explorer offers, in the order people ask about them. */
export const dimensions = [
  "pell",
  "enrollment_intensity",
  "cohort_term",
  "enrollment_type",
  "age_band",
  "gender",
  "race",
] as const;
export type Dimension = (typeof dimensions)[number];

/** Why a number is or isn't shown. A hidden or missing number is never sent as 0. */
export type ResultStatus = "ok" | "suppressed" | "not_yet_observable" | "not_reported";

export type ResultRow = {
  /** The group's value for each grouping, e.g. { pell: "Y" }. Empty for all students. */
  group: Partial<Record<Dimension, string>>;
  numerator: number | null;
  denominator: number | null;
  rate: number | null;
  status: ResultStatus;
  /** Students the measure applies to but couldn't count, e.g. gateway requirement unknown. */
  n_excluded: number | null;
};

export type MeasureDefinition = {
  name: string;
  pdp_name: string;
  what: string;
  how: string;
  who: string;
  limits: string[];
};

export type ResultsMeta = {
  measure: Measure;
  cohort: Cohort;
  group_by: Dimension[];
  definition: MeasureDefinition;
  source: string;
  /** When the source data was loaded, not when the precompute ran. */
  loaded_at: string;
  /** True when the class's year 2 is only partly in the files, so a year-2 rate can still change. */
  provisional?: boolean;
};

export type ResultsResponse = { meta: ResultsMeta; rows: ResultRow[] };

export type ResultsQuery = { measure: Measure; cohort: Cohort; groupBy: Dimension[] };

/** Thrown when a measure, class and grouping combination isn't saved, as the API will do. */
export class NotSavedError extends Error {}

// Placeholder wording until the #3 definitions dictionary exists; the API will send its own.
const interimDefinitions: Record<Measure, MeasureDefinition> = {
  retention: {
    name: "Returned here",
    pdp_name: "Retention",
    what: "Enrolled here in the second academic year, or earned a credential here in the first or second year.",
    how: "Returned or earned a credential here ÷ everyone who entered.",
    who: "Everyone who entered that year: every start term, and first-time, transfer-in and re-admitted students.",
    limits: [
      "Students who moved to another college are not counted as returned.",
      "Spring and summer starters have less time to come back, which pulls the rate down.",
    ],
  },
  gateway_math: {
    name: "Gateway math",
    pdp_name: "Gateway math completion",
    what: "Passed the required first college-level math course in the first year.",
    how: "Passed ÷ students required to take it.",
    who: "Students required to take college-level math when they entered, unless exempt through their program, transfer credit or AP/IB.",
    limits: [
      "A required student with no recorded attempt counts as not passing.",
      "Each college chooses its gateway courses. Until they are mapped in the file, this shows Not reported.",
    ],
  },
  gateway_english: {
    name: "Gateway English",
    pdp_name: "Gateway English completion",
    what: "Passed the required first college-level English course in the first year.",
    how: "Passed ÷ students required to take it.",
    who: "Students required to take college-level English when they entered, unless exempt through their program, transfer credit or AP/IB.",
    limits: [
      "A required student with no recorded attempt counts as not passing.",
      "Each college chooses its gateway courses. Until they are mapped in the file, this shows Not reported.",
    ],
  },
};

const FIXTURE_URL = "/uncf/explorer-fixture.json";

// Until #5 sends `provisional`: the course file covers only part of 2024-25's year 2 (2025-26).
const PROVISIONAL_UNTIL_API: Cohort[] = ["2024-25"];
const YEAR_TWO_MEASURES: Measure[] = ["retention"];

/** [values joined by " x ", numerator, denominator, status, n_excluded], as written by uncf/explorer_fixture.py. */
type FixtureRow = [string, number | null, number | null, Exclude<ResultStatus, "not_reported">, number | null];
/** [values, students, here, moved, none, 4-year, 2-year, not on record, status], as written by uncf/paths_mock.py. */
type Count = number | null;
type FixturePathsRow = [string, Count, Count, Count, Count, Count, Count, Count, ResultStatus];
type Fixture = {
  loaded_at: string;
  rows: Record<string, Record<string, Record<string, FixtureRow[]>>>;
  paths?: Record<string, Record<string, FixturePathsRow[]>>;
};

let fixturePromise: Promise<Fixture> | null = null;

/** Fetch the fixture once per page load. */
function loadFixture(): Promise<Fixture> {
  fixturePromise ??= fetch(FIXTURE_URL).then((response) => {
    if (!response.ok) {
      fixturePromise = null;
      throw new Error(
        "The sample results aren't built yet. From the repo root, run `python -m uncf` and then `python -m uncf.explorer_fixture`.",
      );
    }
    return response.json() as Promise<Fixture>;
  });
  return fixturePromise;
}

/** The saved grouping key, e.g. ["pell", "enrollment_intensity"] -> "enrollment_intensity x pell". */
function groupingKey(groupBy: Dimension[]): string {
  return groupBy.length === 0 ? "all" : [...groupBy].sort().join(" x ");
}

/** Turn one saved row into an API row. */
function toResultRow(row: FixtureRow, savedDimensions: Dimension[]): ResultRow {
  const [values, numerator, denominator, status, nExcluded] = row;
  const group: Partial<Record<Dimension, string>> = {};
  if (values !== "all") {
    values.split(" x ").forEach((value, index) => {
      group[savedDimensions[index]] = value;
    });
  }
  const shown = status === "ok" && numerator !== null && denominator !== null && denominator > 0;
  return {
    group,
    numerator: shown ? numerator : null,
    denominator: shown ? denominator : null,
    rate: shown ? numerator / denominator : null,
    status,
    n_excluded: nExcluded,
  };
}

/** One measure, class and grouping, plus the all-students row. Swap this for the API call when #5 lands. */
export async function loadResults(query: ResultsQuery): Promise<ResultsResponse> {
  const fixture = await loadFixture();
  const byGrouping = fixture.rows[query.measure]?.[query.cohort];
  const key = groupingKey(query.groupBy);
  const saved = byGrouping?.[key];
  const everyone = byGrouping?.all;
  if (!saved || !everyone) {
    throw new NotSavedError("This combination isn't saved yet.");
  }
  const savedDimensions = key === "all" ? [] : (key.split(" x ") as Dimension[]);
  const rows = key === "all" ? saved : [...everyone, ...saved];
  return {
    meta: {
      measure: query.measure,
      cohort: query.cohort,
      group_by: query.groupBy,
      definition: interimDefinitions[query.measure],
      source: "PDP analysis-ready cohort and course files (synthetic sample)",
      loaded_at: fixture.loaded_at,
      provisional: YEAR_TWO_MEASURES.includes(query.measure) && PROVISIONAL_UNTIL_API.includes(query.cohort),
    },
    rows: rows.map((row) => toResultRow(row, savedDimensions)),
  };
}

/** A loader for one query, stable enough to pass to useApiResource. */
export function resultsLoader(query: ResultsQuery): () => Promise<ResultsResponse> {
  return () => loadResults(query);
}

/** The same query for every class, for trend lines. A class that isn't saved comes back as null. */
export async function loadAllCohorts(query: ResultsQuery, load = loadResults): Promise<Record<Cohort, ResultsResponse | null>> {
  const responses = await Promise.all(cohorts.map((cohort) => load({ ...query, cohort }).catch(() => null)));
  return Object.fromEntries(cohorts.map((cohort, index) => [cohort, responses[index]])) as Record<Cohort, ResultsResponse | null>;
}

// ---------------------------------------------------------------------------------------------------
// PROPOSED contract for a year-2 paths endpoint. Nobody owns it yet (see the design's asks), so the
// Explorer reads MOCK rows from the fixture and labels the chart as mock data.

export type CollegeTypeSplit = { four_year: number; two_year: number; not_on_record: number };

export type PathsRow = {
  group: Partial<Record<Dimension, string>>;
  students: number | null;
  /** Enrolled or earned a credential here in year 2 (the retention flag). */
  returned_here: number | null;
  /** At another college instead (persistence without retention). */
  moved: number | null;
  /** No enrollment found here or in the Clearinghouse match. */
  no_enrollment: number | null;
  /** Students who moved, by their most recent other college. Null when fewer than 10 moved. */
  college_type: CollegeTypeSplit | null;
  status: ResultStatus;
};

export type PathsResponse = {
  meta: { cohort: Cohort; group_by: Dimension[]; source: string; loaded_at: string; provisional: boolean; mock: boolean };
  rows: PathsRow[];
};

export type PathsQuery = { cohort: Cohort; groupBy: Dimension[] };

/** Turn one mock paths row into an API-shaped row. */
function toPathsRow(row: FixturePathsRow, savedDimensions: Dimension[]): PathsRow {
  const [values, students, here, moved, none, four, two, notOnRecord, status] = row;
  const group: Partial<Record<Dimension, string>> = {};
  if (values !== "all") {
    values.split(" x ").forEach((value, index) => {
      group[savedDimensions[index]] = value;
    });
  }
  return {
    group,
    students,
    returned_here: here,
    moved,
    no_enrollment: none,
    college_type: four === null || two === null || notOnRecord === null ? null : { four_year: four, two_year: two, not_on_record: notOnRecord },
    status,
  };
}

/** MOCK: year-2 paths for one class and grouping, plus everyone. Swap for the real endpoint once it exists. */
export async function loadPaths(query: PathsQuery): Promise<PathsResponse> {
  const fixture = await loadFixture();
  const byGrouping = fixture.paths?.[query.cohort];
  const key = groupingKey(query.groupBy);
  const saved = byGrouping?.[key];
  const everyone = byGrouping?.all;
  if (!saved || !everyone) {
    throw new NotSavedError("Year-2 paths aren't in the sample results. Rebuild them with `python -m uncf.explorer_fixture`.");
  }
  const savedDimensions = key === "all" ? [] : (key.split(" x ") as Dimension[]);
  const rows = key === "all" ? saved : [...everyone, ...saved];
  return {
    meta: {
      cohort: query.cohort,
      group_by: query.groupBy,
      source: "PDP cohort file: retention and persistence flags, most recent other college (synthetic sample)",
      loaded_at: fixture.loaded_at,
      provisional: PROVISIONAL_UNTIL_API.includes(query.cohort),
      mock: true,
    },
    rows: rows.map((row) => toPathsRow(row, savedDimensions)),
  };
}
