import { cohorts, dimensions, measures, type Cohort, type Dimension, type Measure } from "@/app/(app)/uncf/data";
import { routes } from "@/lib/routes";

export type CardView = { cohort: Cohort; groupBy: Dimension[]; measure: Measure };

/** The card maker's address for an Explorer view, so a card link always opens the same view. */
export function cardHref({ cohort, groupBy, measure }: CardView): string {
  const params = new URLSearchParams({ cohort, group_by: groupBy.join(","), measure });
  return `${routes.uncfCard}?${params.toString()}`;
}

/** Read a view from the address, falling back to Pell grant, 2022-23 and Returned here for anything unknown. */
export function parseCardView(params: Record<string, string | string[] | undefined>): CardView {
  const first = (value: string | string[] | undefined) => (Array.isArray(value) ? value[0] : value) ?? "";
  const cohort = cohorts.find((value) => value === first(params.cohort)) ?? "2022-23";
  const measure = measures.find((value) => value === first(params.measure)) ?? "retention";
  const groupBy = first(params.group_by)
    .split(",")
    .map((part) => dimensions.find((value) => value === part.trim()))
    .filter((value, index, all): value is Dimension => value !== undefined && all.indexOf(value) === index)
    .slice(0, 2);
  return { cohort, measure, groupBy: groupBy.length > 0 ? groupBy : ["pell"] };
}
