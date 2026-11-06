import { Badge } from "@/components/ui/badge";
import { Item, ItemContent, ItemGroup, ItemMedia, ItemTitle } from "@/components/ui/item";
import { cn } from "@/lib/utils";
import type { DictionaryValue } from "./dictionary-types";

/** Structured codes and meanings; dictionary-string parsing belongs to the data adapter. */
export function CodeMeaningList({ values, compact = false }: { values: DictionaryValue[]; compact?: boolean }) {
  return (
    <ItemGroup className={cn(!compact && "sm:grid sm:grid-cols-2")}>
      {values.map(({ code, meaning }) => (
        <Item key={code} role="listitem" size="xs" className="hover:bg-muted">
          <ItemMedia>
            <Badge variant="outline"><code>{code}</code></Badge>
          </ItemMedia>
          <ItemContent>
            <ItemTitle className="line-clamp-none font-normal">{meaning}</ItemTitle>
          </ItemContent>
        </Item>
      ))}
    </ItemGroup>
  );
}
