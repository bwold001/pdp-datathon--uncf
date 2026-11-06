"use client";

import { SearchInput } from "@/components/search-input";

/** Reuses the shared search input while the caller owns dictionary matching. */
export function FieldSearch({ value, onValueChange }: { value: string; onValueChange: (value: string) => void }) {
  return (
    <SearchInput value={value} onChange={onValueChange} label="Search fields" placeholder="e.g. math, credits, Pell" />
  );
}
