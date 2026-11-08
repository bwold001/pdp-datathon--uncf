/** Checks a card's one-sentence takeaway against exactly what the card prints. */

export const MAX_TAKEAWAY = 150;
/** About how many group rows fit on one Letter page with the definition and limits. */
export const MAX_CARD_ROWS = 14;

/** One group on the card: the words a reader might use for it, and its shown rate. */
export type CardGroup = { label: string; phrases: string[]; percent: string | null; hidden: boolean };

export type CardFacts = {
  groups: CardGroup[];
  /** Every percentage printed anywhere on the card, e.g. in a limit. */
  printedRates: string[];
  rowCount: number;
};

export type CheckResult = { id: "matches" | "facts" | "supports" | "privacy" | "fits"; label: string; passed: boolean; note: string };

const CAUSE =
  /\b(because|due to|thanks to|so that|caus(?:e|es|ed|ing)|driv(?:e|es|en|ing)|drove|leads? to|led to|results? in(?! (?:year|the fall|fall|spring|summer|winter))|resulted in|as a result|help(?:s|ed|ing)?|impact(?:s|ed)?|effect of|explains?|which means)\b/i;
// "Since" is a cause word unless a year or term follows it ("since fall 2022").
const SINCE = /\bsince (?!(?:\d{4}|fall|spring|summer|winter|the (?:fall|spring|summer|winter)|year))/i;
const DEFICIT =
  /\b(at[- ]risk|fail(?:s|ed|ing|ure)?|drop(?:s|ped|ping)?[- ]?outs?|stop(?:s|ped|ping)?[- ]?outs?|fell behind|falling behind|fall behind|lag(?:s|ged|ging)? behind|struggl\w*|underperform\w*|low[- ]performing|deficit|lost|weak(?:er|est)?)\b/i;
const PERCENT = /(\d+(?:\.\d+)?)\s?%/g;
const POINTS = /(\d+(?:\.\d+)?)[\s-]*(?:percentage[\s-]*)?points?\b/gi;
// A comparison splits a sentence into clauses, so each rate is tied to the group in its own clause.
const CLAUSE_BREAK = /\s*(?:,\s*)?(?:\bcompared (?:with|to)\b|\bversus\b|\bvs\.?|\bwhile\b|\bwhereas\b|\bbut\b|;)\s*/i;

/** Rates in a piece of text, written the way the card writes them ("58.9%"). */
function percentsIn(text: string): { shown: string; raw: string }[] {
  return Array.from(text.matchAll(PERCENT)).map((match) => ({ shown: `${Number(match[1]).toFixed(1)}%`, raw: match[0] }));
}

/** Groups named in a piece of text, longest phrase first so "no pell grant" wins over "pell grant". */
function groupsIn(text: string, groups: CardGroup[]): CardGroup[] {
  const lower = text.toLowerCase();
  const hits: { group: CardGroup; start: number; end: number }[] = [];
  for (const group of groups) {
    for (const phrase of group.phrases) {
      const pattern = new RegExp(`(^|[^a-z])(${phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})(?![a-z])`, "g");
      for (const match of lower.matchAll(pattern)) {
        const start = (match.index ?? 0) + match[1].length;
        hits.push({ group, start, end: start + phrase.length });
      }
    }
  }
  const kept = hits
    .sort((a, b) => b.end - b.start - (a.end - a.start))
    .filter((hit, index, all) => !all.slice(0, index).some((other) => hit.start < other.end && other.start < hit.end));
  return kept.sort((a, b) => a.start - b.start).map((hit) => hit.group);
}

/** Small whole counts (1 to 9) that could point to a few students; "year 2" and the like don't count. */
function smallCountsIn(text: string): string[] {
  const found: string[] = [];
  for (const match of text.matchAll(/(^|[^\d.,])(\d+)(?![\d.,]*\s?%)(?![\d.,])/g)) {
    const value = Number(match[2]);
    const before = text.slice(Math.max(0, (match.index ?? 0) - 6), (match.index ?? 0) + match[1].length).toLowerCase();
    const after = text.slice((match.index ?? 0) + match[0].length).toLowerCase();
    if (value >= 1 && value <= 9 && !/(year|grade|term|step) ?$/.test(before) && !/^-?year/.test(after)) found.push(match[2]);
  }
  return found;
}

/** Run every check. A check that fails says what to change. */
export function checkTakeaway(text: string, facts: CardFacts): CheckResult[] {
  const quoted = percentsIn(text);
  const onCard = new Set([...facts.groups.flatMap((group) => (group.percent ? [group.percent] : [])), ...facts.printedRates]);
  const notOnCard = quoted.filter((rate) => !onCard.has(rate.shown)).map((rate) => rate.raw);

  const wrongGroup: string[] = [];
  for (const clause of text.split(CLAUSE_BREAK)) {
    const rates = percentsIn(clause).filter((rate) => onCard.has(rate.shown));
    const named = groupsIn(clause, facts.groups);
    rates.forEach((rate, index) => {
      const group = named[Math.min(index, named.length - 1)];
      if (group && group.percent && group.percent !== rate.shown) wrongGroup.push(`${rate.raw} isn't the rate for ${group.label} on the card`);
    });
  }

  const gapIssues: string[] = [];
  for (const match of text.matchAll(POINTS)) {
    if (quoted.length < 2) {
      gapIssues.push("Quote both rates when you give a gap");
      continue;
    }
    const expected = Math.round(Math.abs(parseFloat(quoted[0].shown) - parseFloat(quoted[1].shown)) * 10) / 10;
    if (Math.abs(Number(match[1]) - expected) > 0.05) {
      gapIssues.push(`The gap between ${quoted[0].shown} and ${quoted[1].shown} is ${expected.toFixed(1)} points, not ${match[1]}`);
    }
  }

  const empty = text.trim().length === 0;
  const cause = (text.match(CAUSE) ?? text.match(SINCE))?.[0];
  const deficit = text.match(DEFICIT)?.[0];
  const small = smallCountsIn(text);
  const hiddenNamed = groupsIn(text, facts.groups.filter((group) => group.hidden)).map((group) => group.label);
  const matches = !empty && quoted.length > 0 && notOnCard.length === 0 && wrongGroup.length === 0 && gapIssues.length === 0;
  const tooManyRows = facts.rowCount > MAX_CARD_ROWS;

  return [
    {
      id: "matches",
      label: "Matches the card.",
      passed: matches,
      note: empty
        ? "Write one sentence that quotes at least one rate from the card."
        : quoted.length === 0
          ? "Quote at least one rate from the card so readers can check it."
          : notOnCard.length > 0
            ? `Not on the card: ${notOnCard.join(", ")}. Use the rates exactly as shown.`
            : wrongGroup.length > 0
              ? `${wrongGroup[0]}.`
              : gapIssues.length > 0
                ? `${gapIssues[0]}.`
                : "Every rate is on the card, next to the group it describes.",
    },
    {
      id: "facts",
      label: "States facts, not causes.",
      passed: !cause,
      note: cause ? `Remove “${cause.trim()}”. The data shows a gap, not why it exists.` : "No cause words found.",
    },
    {
      id: "supports",
      label: "Supports students.",
      passed: !deficit,
      note: deficit ? `Replace “${deficit}” with a neutral description, such as “did not return” or “did not pass.”` : "No labels like “at-risk” or “failing.”",
    },
    {
      id: "privacy",
      label: "Protects privacy.",
      passed: hiddenNamed.length === 0 && small.length === 0,
      note:
        hiddenNamed.length > 0
          ? `${hiddenNamed[0]} is hidden on the card. Don't describe it.`
          : small.length > 0
            ? `Small counts like ${small[0]} can point to a few students. Use a rate from the card.`
            : "No small counts or hidden groups in the sentence.",
    },
    {
      id: "fits",
      label: "Fits on one page.",
      passed: text.length <= MAX_TAKEAWAY && !tooManyRows,
      note: tooManyRows
        ? `This view has ${facts.rowCount} rows; a card fits about ${MAX_CARD_ROWS}. Go back and pick one grouping.`
        : text.length > MAX_TAKEAWAY
          ? `Shorten it by ${text.length - MAX_TAKEAWAY} characters.`
          : `Up to ${MAX_TAKEAWAY} characters fit.`,
    },
  ];
}
