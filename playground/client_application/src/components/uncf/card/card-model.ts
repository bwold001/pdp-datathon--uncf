import { isGatewayMeasure, type ResultsResponse } from "@/app/(app)/uncf/data";
import { buildBars, formatPercent, percentOf, SMALL_GROUP } from "@/components/uncf/explorer/bars";
import { cohortLabel, dimensionInfo, measureNames, measureVerbs, valuePhrases, whoPhrase } from "@/components/uncf/explorer/labels";

import type { CardFacts, CardGroup } from "./takeaway-checks";

export type CardRow = {
  key: string;
  label: string;
  state: "ok" | "hidden" | "not_yet" | "not_reported";
  percent: number | null;
  numerator: number | null;
  denominator: number | null;
  isUnknown: boolean;
  isAll: boolean;
};

export type CardContent = {
  eyebrow: string;
  caption: string;
  compared: string;
  baseLabel: string;
  baseCount: string;
  rows: CardRow[];
  what: string;
  who: string;
  limits: string[];
  footnote: string;
  suggested: string;
  facts: CardFacts;
};

/** Everything one card prints, from the same response the Explorer draws, so the numbers always match. */
export function buildCard(response: ResultsResponse): CardContent {
  const { meta } = response;
  const isGateway = isGatewayMeasure(meta.measure);
  const { everyone, sections } = buildBars(response);
  const groupBy = meta.group_by;

  // Group rows first (pairs as "Pell grant · Full-time"), then all students last, as a total.
  const rows: CardRow[] = sections.flatMap((section) =>
    [...section.bars, ...section.hidden].map((bar) => ({
      key: `${section.key}|${bar.key}`,
      label: section.heading ? `${section.heading} · ${bar.label}` : bar.label,
      state: bar.state,
      percent: bar.percent,
      numerator: bar.numerator,
      denominator: bar.denominator,
      isUnknown: bar.isUnknown,
      isAll: false,
    })),
  );
  if (everyone) {
    rows.push({ key: "all", label: "All students", state: everyone.state, percent: everyone.percent, numerator: everyone.numerator, denominator: everyone.denominator, isUnknown: false, isAll: true });
  }

  // Words a reader might use for each single-grouping row, for the takeaway checks.
  const phrasesFor = (row: CardRow): string[] => {
    if (row.isAll) return ["all students", "every student", "everyone", "overall"];
    if (groupBy.length !== 1) return [row.label.toLowerCase()];
    const value = response.rows.find((candidate) => (candidate.group[groupBy[0]] ?? "") === row.key.split("|")[1])?.group[groupBy[0]];
    return value ? valuePhrases(groupBy[0], value) : [row.label.toLowerCase()];
  };
  const groups: CardGroup[] = rows.map((row) => ({
    label: row.label,
    phrases: phrasesFor(row),
    percent: row.percent === null ? null : formatPercent(row.percent),
    hidden: row.state === "hidden",
  }));

  const everyoneRow = response.rows.find((row) => Object.keys(row.group).length === 0);
  const leftOut = everyoneRow?.n_excluded ?? 0;
  const limits = [
    ...(meta.provisional ? ["Year 2 for this class is still arriving: the course file covers only part of it, so this can still change."] : []),
    ...meta.definition.limits,
    ...(isGateway && leftOut > 0 ? [`${leftOut.toLocaleString("en-US")} students with an unknown requirement or result are left out, not counted as 0.`] : []),
    "A gap shows a difference between groups, not its cause.",
  ].slice(0, 3);

  const cohortText = cohortLabel(meta.cohort);
  const compared = groupBy.map((dimension) => dimensionInfo[dimension].label).join(" and ");
  return {
    eyebrow: `${measureNames[meta.measure]} (PDP: ${meta.definition.pdp_name}) · Entered ${cohortText}`.toUpperCase(),
    caption: `${meta.definition.what} By ${groupBy.map((dimension) => dimensionInfo[dimension].phrase).join(" and ")}.`,
    compared,
    baseLabel: isGateway ? "Required to take it" : "Students",
    baseCount: everyone?.denominator != null ? everyone.denominator.toLocaleString("en-US") : "—",
    rows,
    what: meta.definition.what,
    who: meta.definition.who,
    limits,
    footnote:
      "Bars run from 0% to 100%." +
      (rows.some((row) => row.isUnknown) ? " Unknown: the value is missing from the file." : "") +
      (rows.some((row) => row.state === "hidden") ? " A dashed row is hidden to protect privacy; it does not mean 0." : ""),
    suggested: suggestedSentence(response, rows),
    facts: { groups, printedRates: [], rowCount: rows.length },
  };
}

/** A takeaway built from the card's own rows, so it passes the checks. Names groups only when exactly two compare. */
function suggestedSentence(response: ResultsResponse, rows: CardRow[]): string {
  const { meta } = response;
  const isGateway = isGatewayMeasure(meta.measure);
  const verb = measureVerbs[meta.measure];
  const groupBy = meta.group_by;
  const everyone = rows.find((row) => row.isAll);
  const eligible = rows
    .filter((row) => !row.isAll && !row.isUnknown && row.state === "ok" && (row.denominator ?? 0) >= SMALL_GROUP)
    .sort((a, b) => (b.percent ?? 0) - (a.percent ?? 0));

  if (groupBy.length === 1 && eligible.length === 2) {
    const [high, low] = eligible;
    const who = (row: CardRow) => {
      const value = response.rows.find((candidate) => (candidate.group[groupBy[0]] ?? "") === row.key.split("|")[1])?.group[groupBy[0]] ?? "";
      return whoPhrase(groupBy[0], value);
    };
    const required = isGateway ? " required to take it" : "";
    const long = `${formatPercent(high.percent as number)} of ${who(high)}${required} ${verb}, compared with ${formatPercent(low.percent as number)} of ${who(low)}${required}.`;
    if (long.length <= 150) return long;
    return `${formatPercent(high.percent as number)} of ${who(high)} ${verb}, compared with ${formatPercent(low.percent as number)} of ${who(low)}.`;
  }
  if (!everyone || everyone.state !== "ok" || everyone.numerator === null || everyone.denominator === null) return "";
  const all = formatPercent(percentOf(everyone.numerator, everyone.denominator));
  const base = `${all} of students who entered in ${cohortLabel(meta.cohort)}${isGateway ? " and were required to take it" : ""} ${verb}.`;
  if (eligible.length < 3) return base;
  const unit = groupBy.length === 2 ? "Combinations" : "Groups";
  return `${base} ${unit} of ${SMALL_GROUP} or more ranged from ${formatPercent(eligible[eligible.length - 1].percent as number)} to ${formatPercent(eligible[0].percent as number)}.`;
}
