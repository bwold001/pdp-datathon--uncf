import { CardMaker } from "@/components/uncf/card/card-maker";
import { parseCardView } from "@/components/uncf/card/card-link";

type CardFromAddressProps = { searchParams: Promise<Record<string, string | string[] | undefined>> };

/** Reads the view from the address, then hands it to the card maker. */
export async function CardFromAddress({ searchParams }: CardFromAddressProps) {
  const view = parseCardView(await searchParams);
  return <CardMaker cohort={view.cohort} groupBy={view.groupBy} initialMeasure={view.measure} />;
}
