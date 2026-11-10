"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

import { filterValueLabel } from "./cohort-filters";
import type { CohortFilterDefinition } from "./explorer-config";
import { explorerFontClass } from "./explorer-fonts";
import { explorerLinkButton, explorerPrimaryButton } from "./explorer-styles";

type FilterSelectProps = {
  definition: CohortFilterDefinition;
  /** The applied value; null means "All". */
  value: string | null;
  onChange: (value: string | null) => void;
  /** Students with each value, from the API: null is a group under 10. Left out while loading. */
  counts?: Record<string, number | null>;
  disabled?: boolean;
};

const SMALL_GROUPS_HINT = "Groups under 10 students are hidden to protect privacy.";

/** One cohort filter: a button that opens a list of values. A pick only counts once Apply is pressed. */
export function FilterSelect({ definition, value, onChange, counts, disabled }: FilterSelectProps) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<string | null>(value);
  const [search, setSearch] = useState("");
  const labelId = useId();
  const triggerId = useId();
  const radioName = useId();
  // A filter with a default (the cohort year) always has a value, so it offers no "All".
  const offersAll = definition.defaultValue === undefined;

  /** Each time the list opens, it starts from the applied value. */
  function handleOpenChange(nextOpen: boolean) {
    if (nextOpen) {
      setDraft(value);
      setSearch("");
    }
    setOpen(nextOpen);
  }

  /** Use the picked value and close the list. */
  function apply() {
    onChange(draft);
    setOpen(false);
  }

  const needle = search.trim().toLowerCase();
  const shownOptions = definition.options.filter((option) => option.label.toLowerCase().includes(needle));

  return (
    <div className="flex flex-col gap-1">
      <span id={labelId} className="text-[13px] font-medium text-(--uncf-ink-2)">
        {definition.label}
      </span>
      <Popover open={open} onOpenChange={handleOpenChange}>
        <PopoverTrigger
          id={triggerId}
          aria-labelledby={`${labelId} ${triggerId}`}
          disabled={disabled}
          className="group flex w-35 cursor-pointer items-center justify-between gap-2 rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-3 py-2.25 text-left disabled:cursor-default data-popup-open:border-2 data-popup-open:border-(--uncf-blue) data-popup-open:px-2.75 data-popup-open:py-2 sm:w-39"
        >
          <span className="truncate">{filterValueLabel(definition, value)}</span>
          <ChevronDown
            className="size-3.5 shrink-0 transition-transform group-data-popup-open:rotate-180 motion-reduce:transition-none"
            aria-hidden
          />
        </PopoverTrigger>
        <PopoverContent
          align="start"
          sideOffset={6}
          className={cn(
            explorerFontClass,
            "w-75 max-w-[calc(100vw-32px)] gap-0 rounded-lg border border-(--uncf-line) bg-(--uncf-surface) p-2 text-[15px] text-(--uncf-ink) shadow-[0_10px_30px_rgba(0,0,0,.12)] ring-0 [color-scheme:light]",
          )}
        >
          {definition.searchable && (
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search…"
              aria-label={`Search ${definition.label}`}
              className="mb-1.5 w-full rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-2.5 py-2"
            />
          )}
          <fieldset className="max-h-90 overflow-y-auto">
            <legend className="sr-only">{definition.label}</legend>
            {offersAll && (
              <FilterOptionRow name={radioName} label="All" checked={draft === null} onSelect={() => setDraft(null)} bold />
            )}
            {shownOptions.map((option) => {
              const count = counts?.[option.value];
              // Under 10 students (or none): too small to show, so it can't be picked.
              const tooSmall = counts !== undefined && (count === null || count === 0);
              return (
                <FilterOptionRow
                  key={option.value}
                  name={radioName}
                  label={option.label}
                  count={counts === undefined ? undefined : count === null ? "under 10" : (count ?? 0).toLocaleString("en-US")}
                  checked={draft === option.value}
                  disabled={tooSmall && draft !== option.value}
                  onSelect={() => setDraft(option.value)}
                />
              );
            })}
            {shownOptions.length === 0 && <p className="px-2 py-2.25 text-(--uncf-ink-3)">No matches.</p>}
          </fieldset>
          <p className="mx-1.5 mt-1.5 text-[13px] text-(--uncf-ink-3)">{definition.hint ?? SMALL_GROUPS_HINT}</p>
          <div className="mt-1 flex items-center justify-between border-t border-(--uncf-line) px-1.5 pt-2.5 pb-1">
            <button type="button" className={explorerLinkButton} onClick={() => setDraft(definition.defaultValue ?? null)}>
              Clear
            </button>
            <button type="button" className={explorerPrimaryButton} onClick={apply}>
              Apply
            </button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}

type FilterOptionRowProps = {
  name: string;
  label: string;
  checked: boolean;
  onSelect: () => void;
  count?: string;
  disabled?: boolean;
  bold?: boolean;
};

/** One value in the list, as a radio button, with its student count on the right. */
function FilterOptionRow({ name, label, checked, onSelect, count, disabled, bold }: FilterOptionRowProps) {
  return (
    <label
      className={cn(
        "flex cursor-pointer items-center gap-2.5 rounded-sm border-b border-(--uncf-line) px-2 py-2.25 last-of-type:border-b-0",
        checked && "bg-(--uncf-blue-tint)",
        bold && "font-semibold",
        disabled && "cursor-not-allowed text-(--uncf-ink-3) opacity-60",
      )}
    >
      <input
        type="radio"
        name={name}
        checked={checked}
        disabled={disabled}
        onChange={onSelect}
        className="m-0 size-4.5 shrink-0 accent-(--uncf-blue)"
      />
      {label}
      {count !== undefined && <span className="uncf-num ml-auto text-[13px] whitespace-nowrap text-(--uncf-ink-3)">{count}</span>}
    </label>
  );
}
