"use client";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

type TableLanguageToggleProps = { value: "plain" | "analyst"; onChange: (value: "plain" | "analyst") => void };

/** Lets the caller choose plain-language or source-column table headings. */
export function TableLanguageToggle({ value, onChange }: TableLanguageToggleProps) {
  return (
    <ToggleGroup aria-label="Table language" multiple={false} value={[value]} onValueChange={(values) => {
      const next = values[0];
      if (next === "plain" || next === "analyst") onChange(next);
    }} variant="outline" className="max-w-full flex-wrap">
      <ToggleGroupItem value="plain">Plain language</ToggleGroupItem>
      <ToggleGroupItem value="analyst">Analyst</ToggleGroupItem>
    </ToggleGroup>
  );
}
