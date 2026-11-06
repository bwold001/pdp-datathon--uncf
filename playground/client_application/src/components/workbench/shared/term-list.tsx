import { Fragment } from "react";
import { Item, ItemContent, ItemDescription, ItemGroup, ItemSeparator, ItemTitle } from "@/components/ui/item";
import type { DescribedItem } from "./dictionary-types";

/** Read-only term rows; the hover matches Item's link hover without making rows clickable. */
export function TermList({ terms }: { terms: DescribedItem[] }) {
  return (
    <ItemGroup>
      {terms.map((term, index) => (
        <Fragment key={term.id}>
          {index > 0 && <ItemSeparator aria-hidden="true" className="my-0" />}
          <Item role="listitem" size="sm" className="hover:bg-muted">
            <ItemContent>
              <ItemTitle className="line-clamp-none">{term.label}</ItemTitle>
              <ItemDescription className="line-clamp-none">{term.description}</ItemDescription>
            </ItemContent>
          </Item>
        </Fragment>
      ))}
    </ItemGroup>
  );
}
