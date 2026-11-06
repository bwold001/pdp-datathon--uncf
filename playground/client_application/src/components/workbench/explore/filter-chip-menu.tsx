"use client";

import { useId, useState } from "react";
import { SearchInput } from "@/components/search-input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Popover, PopoverContent, PopoverTitle, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";

export type FilterOption = { value: string; label: string; count: number };
export type FilterChipMenuProps = {
  label: string;
  question: string;
  options: FilterOption[];
  selectedValues: string[];
  onSelectionChange: (values: string[]) => void;
  onExplain: () => void;
  searchable?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
};

/** Owns menu and search state while the caller controls selected filter values. */
export function FilterChipMenu({ label, question, options, selectedValues, onSelectionChange, onExplain, searchable = true, open, onOpenChange }: FilterChipMenuProps) {
  const id = useId();
  const [localOpen, setLocalOpen] = useState(false);
  const [search, setSearch] = useState("");
  /** Supports either local menu state or an explicit controlled open prop. */
  function changeOpen(next: boolean) {
    setLocalOpen(next);
    onOpenChange?.(next);
  }
  const selectedLabel = options.find((option) => option.value === selectedValues[0])?.label ?? selectedValues[0];
  const sorted = options.filter((option) => !searchable || option.label.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, "en-US"));
  return (
    <Popover open={open ?? localOpen} onOpenChange={changeOpen}>
      <PopoverTrigger render={<Button variant="outline" />}>
        {label}: {selectedValues.length ? selectedLabel : "Any"}
        {selectedValues.length > 1 && <Badge variant="secondary">+{(selectedValues.length - 1).toLocaleString("en-US")}</Badge>}
      </PopoverTrigger>
      <PopoverContent align="start" className="max-w-[calc(100vw-2rem)]">
        <PopoverTitle>{question}</PopoverTitle>
        {searchable && <SearchInput value={search} onChange={setSearch} placeholder={`Search ${label.toLowerCase()}`} label={`Search ${label} options`} />}
        <fieldset className="min-w-0">
          <legend className="sr-only">{label} options</legend>
          <ScrollArea className="h-52">
            <div className="flex flex-col gap-3 p-2">
              {sorted.map((option, index) => (
                <label key={option.value} htmlFor={`${id}-${index}`} className="flex items-center gap-3">
                  <Checkbox id={`${id}-${index}`} checked={selectedValues.includes(option.value)} onCheckedChange={(checked) => onSelectionChange(checked ? [...selectedValues, option.value] : selectedValues.filter((value) => value !== option.value))} />
                  <span className="min-w-0 flex-1 break-words">{option.label}</span>
                  <span className="tabular-nums text-muted-foreground">{option.count.toLocaleString("en-US")}</span>
                </label>
              ))}
              {sorted.length === 0 && <p role="status">No options match</p>}
            </div>
          </ScrollArea>
        </fieldset>
        <div className="flex flex-wrap justify-between gap-2">
          <Button variant="ghost" size="sm" onClick={() => { changeOpen(false); onExplain(); }}>
            What is this?
          </Button>
          <Button variant="ghost" size="sm" disabled={selectedValues.length === 0} onClick={() => onSelectionChange([])}>
            Clear
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

/** Groups filter chips and exposes the caller's clear-all action. */
export function FilterBar({ children, hasFilters, onClearAll }: { children: React.ReactNode; hasFilters: boolean; onClearAll: () => void }) {
  return (
    <section aria-label="Filter students" className="flex flex-wrap items-center gap-2">
      {children}
      <Button variant="ghost" size="sm" disabled={!hasFilters} onClick={onClearAll}>Clear all</Button>
    </section>
  );
}
