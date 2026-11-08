import type { Dimension, MeasureDefinition, PathsQuery, PathsResponse, PathsRow, ResultRow, ResultsQuery, ResultsResponse, ResultStatus } from "@/app/(app)/uncf/data";

/** Small, hand-written responses for stories and tests, in the #5 API's shape. Synthetic numbers. */

const definition: MeasureDefinition = {
  name: "Returned here",
  pdp_name: "Retention",
  what: "Enrolled here in the second academic year, or earned a credential here.",
  how: "Returned or earned a credential here ÷ everyone who entered.",
  who: "Everyone who entered that year.",
  limits: ["Spring and summer starters have less time to come back."],
};

const gatewayDefinition: MeasureDefinition = {
  name: "Gateway math",
  pdp_name: "Gateway math completion",
  what: "Passed the required first college-level math course in the first year.",
  how: "Passed ÷ students required to take it.",
  who: "Students required to take college-level math when they entered.",
  limits: ["A required student with no recorded attempt counts as not passing."],
};

/** One row; a status other than "ok" gets nulls, as the API sends it. */
function row(group: Partial<Record<Dimension, string>>, numerator: number | null, denominator: number | null, status: ResultStatus = "ok", nExcluded: number | null = 0): ResultRow {
  const shown = status === "ok" && numerator !== null && denominator !== null;
  return {
    group,
    numerator: shown ? numerator : null,
    denominator: shown ? denominator : null,
    rate: shown ? (numerator as number) / (denominator as number) : null,
    status,
    n_excluded: shown ? nExcluded : null,
  };
}

/** A response for one grouping, with the all-students row first. */
function response(query: Pick<ResultsQuery, "measure" | "groupBy">, rows: ResultRow[]): ResultsResponse {
  return {
    meta: {
      measure: query.measure,
      cohort: "2022-23",
      group_by: query.groupBy,
      definition: query.measure === "retention" ? definition : gatewayDefinition,
      source: "PDP analysis-ready cohort and course files (synthetic sample)",
      loaded_at: "2026-11-08T22:57:20",
    },
    rows,
  };
}

export const retentionByPell = response({ measure: "retention", groupBy: ["pell"] }, [
  row({}, 1414, 2617),
  row({ pell: "Y" }, 514, 873),
  row({ pell: "N" }, 848, 1578),
  row({ pell: "UNKNOWN" }, 52, 166),
]);

export const retentionByGender = response({ measure: "retention", groupBy: ["gender"] }, [
  row({}, 1414, 2617),
  row({ gender: "F" }, 767, 1410),
  row({ gender: "M" }, 607, 1103),
  row({ gender: "X" }, null, null, "suppressed"),
  row({ gender: "UNKNOWN" }, 39, 103),
]);

export const gatewayMathByPell = response({ measure: "gateway_math", groupBy: ["pell"] }, [
  row({}, 304, 1149, "ok", 518),
  row({ pell: "Y" }, 139, 448, "ok", 165),
  row({ pell: "N" }, 153, 651, "ok", 280),
  row({ pell: "UNKNOWN" }, 12, 50, "ok", 73),
]);

export const retentionByPellAndLoad = response({ measure: "retention", groupBy: ["pell", "enrollment_intensity"] }, [
  row({}, 1414, 2617),
  row({ pell: "Y", enrollment_intensity: "Full-time" }, 302, 465),
  row({ pell: "Y", enrollment_intensity: "Part-time" }, 207, 396),
  row({ pell: "Y", enrollment_intensity: "UNKNOWN" }, 5, 12),
  row({ pell: "N", enrollment_intensity: "Full-time" }, 344, 517),
  row({ pell: "N", enrollment_intensity: "Part-time" }, 504, 1056),
  row({ pell: "N", enrollment_intensity: "UNKNOWN" }, null, null, "suppressed"),
]);

/** A school's first file: the newest class hasn't reached year 2, and gateway courses aren't mapped. */
export const notYetAndNotReported = response({ measure: "gateway_math", groupBy: ["pell"] }, [
  row({}, null, null, "not_reported"),
  row({ pell: "Y" }, null, null, "not_reported"),
  row({ pell: "N" }, null, null, "not_yet_observable"),
]);

/** A loader that answers from the samples above, as the page's loader would from the API. */
export async function loadSample(query: ResultsQuery): Promise<ResultsResponse> {
  const key = `${query.measure}:${query.groupBy.join("+")}`;
  const samples: Record<string, ResultsResponse> = {
    "retention:pell": retentionByPell,
    "retention:gender": retentionByGender,
    "gateway_math:pell": gatewayMathByPell,
    "retention:pell+enrollment_intensity": retentionByPellAndLoad,
  };
  const found = samples[key];
  if (!found) throw new Error("This combination isn't saved yet.");
  return { ...found, meta: { ...found.meta, cohort: query.cohort } };
}

/** One paths row; hidden groups are all blank. */
function pathsRow(group: Partial<Record<Dimension, string>>, counts: [number, number, number] | null, split: [number, number, number] | null = null): PathsRow {
  if (!counts) return { group, students: null, returned_here: null, moved: null, no_enrollment: null, college_type: null, status: "suppressed" };
  const [here, moved, none] = counts;
  return {
    group,
    students: here + moved + none,
    returned_here: here,
    moved,
    no_enrollment: none,
    college_type: split ? { four_year: split[0], two_year: split[1], not_on_record: split[2] } : null,
    status: "ok",
  };
}

/** Mock year-2 paths, as the paths chart reads them. */
function pathsResponse(groupBy: Dimension[], rows: PathsRow[]): PathsResponse {
  return {
    meta: { cohort: "2022-23", group_by: groupBy, source: "Synthetic sample", loaded_at: "2026-11-08T22:57:20", provisional: false, mock: true },
    rows,
  };
}

export const pathsByPell = pathsResponse(["pell"], [
  pathsRow({}, [1414, 343, 860], [210, 74, 59]),
  pathsRow({ pell: "Y" }, [514, 69, 290], [31, 29, 9]),
  pathsRow({ pell: "N" }, [848, 227, 503], [150, 30, 47]),
  pathsRow({ pell: "UNKNOWN" }, [52, 47, 67], [29, 15, 3]),
]);

export const pathsByGender = pathsResponse(["gender"], [
  pathsRow({}, [1414, 343, 860], [210, 74, 59]),
  pathsRow({ gender: "F" }, [767, 196, 447], [121, 50, 25]),
  pathsRow({ gender: "M" }, [607, 133, 363], [80, 20, 33]),
  pathsRow({ gender: "X" }, null),
]);

/** A paths loader that answers from the samples above. */
export async function loadPathsSample(query: PathsQuery): Promise<PathsResponse> {
  const found = { pell: pathsByPell, gender: pathsByGender }[query.groupBy.join("+")];
  if (!found) throw new Error("Year-2 paths aren't in the sample results.");
  return { ...found, meta: { ...found.meta, cohort: query.cohort } };
}
