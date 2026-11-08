import type { Dimension, Measure } from "@/app/(app)/uncf/data";

/** Plain-language names for each grouping, how it reads in a sentence, and its values in display order. */
export const dimensionInfo: Record<
  Dimension,
  { label: string; phrase: string; values: { value: string; label: string }[] }
> = {
  pell: {
    label: "Pell grant",
    phrase: "Pell grant",
    values: [
      { value: "Y", label: "Pell grant" },
      { value: "N", label: "No Pell grant" },
      { value: "UNKNOWN", label: "Pell status unknown" },
    ],
  },
  enrollment_intensity: {
    label: "Full- or part-time",
    phrase: "full- or part-time status",
    values: [
      { value: "Full-time", label: "Full-time" },
      { value: "Part-time", label: "Part-time" },
      { value: "UNKNOWN", label: "Full- or part-time unknown" },
    ],
  },
  cohort_term: {
    label: "Start term",
    phrase: "start term",
    values: [
      { value: "Fall", label: "Fall start" },
      { value: "Winter", label: "Winter start" },
      { value: "Spring", label: "Spring start" },
      { value: "Summer", label: "Summer start" },
      { value: "UNKNOWN", label: "Start term unknown" },
    ],
  },
  enrollment_type: {
    label: "Entry type",
    phrase: "entry type",
    values: [
      { value: "First-time", label: "First-time" },
      { value: "Transfer-in", label: "Transfer-in" },
      { value: "Re-admit", label: "Re-admitted" },
      { value: "UNKNOWN", label: "Entry type unknown" },
    ],
  },
  age_band: {
    label: "Age at entry",
    phrase: "age at entry",
    values: [
      { value: "20 and younger", label: "20 or younger" },
      { value: "> 20-24", label: "21 to 24" },
      { value: "Older than 24", label: "Older than 24" },
      { value: "UNKNOWN", label: "Age unknown" },
    ],
  },
  gender: {
    label: "Gender",
    phrase: "gender",
    values: [
      { value: "F", label: "Female" },
      { value: "M", label: "Male" },
      { value: "X", label: "Gender X" },
      { value: "P", label: "Gender P" },
      { value: "UNKNOWN", label: "Gender unknown" },
    ],
  },
  race: {
    label: "Race",
    phrase: "race",
    values: [
      { value: "Black or African American", label: "Black or African American" },
      { value: "Hispanic", label: "Hispanic" },
      { value: "White", label: "White" },
      { value: "Asian", label: "Asian" },
      { value: "American Indian or Alaska Native", label: "American Indian or Alaska Native" },
      { value: "Native Hawaiian or Other Pacific Islander", label: "Native Hawaiian or Other Pacific Islander" },
      { value: "Two or More Races", label: "Two or more races" },
      { value: "Nonresident alien", label: "U.S. nonresident" },
      { value: "UNKNOWN", label: "Race unknown" },
    ],
  },
};

/** Plain-language outcome names first; the PDP name comes from the definition. */
export const measureNames: Record<Measure, string> = {
  retention: "Returned here",
  gateway_math: "Gateway math",
  gateway_english: "Gateway English",
};

/** What a rate means in a sentence, e.g. "58.9% of Pell recipients came back or earned a credential here". */
export const measureVerbs: Record<Measure, string> = {
  retention: "came back or earned a credential here in year 2",
  gateway_math: "passed gateway math in year 1",
  gateway_english: "passed gateway English in year 1",
};

/** A value's label, e.g. ("pell", "Y") -> "Pell grant". Falls back to the raw value. */
export function valueLabel(dimension: Dimension, value: string): string {
  return dimensionInfo[dimension].values.find((entry) => entry.value === value)?.label ?? value;
}

/** Where a value sits in its grouping's display order; unlisted values go last. */
export function valueOrder(dimension: Dimension, value: string): number {
  const index = dimensionInfo[dimension].values.findIndex((entry) => entry.value === value);
  return index === -1 ? Number.MAX_SAFE_INTEGER : index;
}

/** A class year as people write it, e.g. "2022-23" -> "2022–23". */
export function cohortLabel(cohort: string): string {
  return cohort.replace("-", "–");
}

/** How a group reads in a sentence, e.g. "Pell grant recipients". Groups not listed fall back to their label. */
const WHO: Partial<Record<Dimension, Record<string, string>>> = {
  pell: { Y: "Pell grant recipients", N: "students without a Pell grant" },
  enrollment_intensity: { "Full-time": "full-time students", "Part-time": "part-time students" },
  cohort_term: { Fall: "fall starters", Winter: "winter starters", Spring: "spring starters", Summer: "summer starters" },
  enrollment_type: { "First-time": "first-time students", "Transfer-in": "transfer-in students", "Re-admit": "re-admitted students" },
  age_band: { "20 and younger": "students 20 or younger at entry", "> 20-24": "students 21 to 24 at entry", "Older than 24": "students older than 24 at entry" },
  gender: { F: "female students", M: "male students" },
};

/** Other ways people write a group, so the card's checks can tell which group a sentence names. */
const ALSO: Partial<Record<Dimension, Record<string, string[]>>> = {
  pell: {
    Y: ["pell recipients", "with pell", "with a pell grant", "received pell", "received a pell grant"],
    N: ["without pell", "without a pell grant", "no pell", "not pell", "non-pell"],
    UNKNOWN: ["unknown pell", "no pell status"],
  },
  enrollment_intensity: { "Full-time": ["full-time", "full time"], "Part-time": ["part-time", "part time"] },
  enrollment_type: { "First-time": ["first-time", "first time"], "Transfer-in": ["transfer-in", "transfer students"], "Re-admit": ["re-admitted", "readmitted"] },
  gender: { F: ["female", "women"], M: ["male", "men"] },
};

/** A group as it reads in a sentence, e.g. ("pell", "N") -> "students without a Pell grant". */
export function whoPhrase(dimension: Dimension, value: string): string {
  return WHO[dimension]?.[value] ?? `students in “${valueLabel(dimension, value)}”`;
}

/** Every way a group might be written, lower case. */
export function valuePhrases(dimension: Dimension, value: string): string[] {
  return [valueLabel(dimension, value).toLowerCase(), ...(WHO[dimension]?.[value] ? [WHO[dimension][value].toLowerCase()] : []), ...(ALSO[dimension]?.[value] ?? [])];
}
