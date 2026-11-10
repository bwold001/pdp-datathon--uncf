"use client";

import { Dialog } from "@base-ui/react/dialog";
import { ChevronDown, ChevronLeft, ChevronRight, Plus, X } from "lucide-react";
import { useState } from "react";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

import { type CohortFilters, filterValueLabel, sentenceWord } from "./cohort-filters";
import { type CohortFilterDefinition, filterGroups } from "./explorer-config";
import { explorerFontClass } from "./explorer-fonts";
import { explorerLinkButton, explorerPrimaryButton } from "./explorer-styles";
import { hiddenCount } from "./small-groups";

/** Students with each value of a filter, from the API: null is a group under the API's min_students. */
export type ValueCounts = Record<string, number | null>;

/** One value in a list: what it's called, its students, and whether it's picked or too small to pick. */
type OptionRow = { value: string | null; label: string; count?: string; disabled: boolean; selected: boolean };

/** A filter's values as rows: "Any" (or its "All" words) first unless it always has a value. */
function optionRows(definition: CohortFilterDefinition, value: string | null, counts?: ValueCounts, minStudents = 1): OptionRow[] {
  const rows: OptionRow[] = [];
  if (!definition.required) {
    rows.push({ value: null, label: definition.allLabel ?? "Any", disabled: false, selected: value === null });
  }
  for (const option of definition.options) {
    const count = counts?.[option.value];
    // Under minStudents (or none): too small to show, so it can't be picked.
    const tooSmall = counts !== undefined && (count === null || count === 0 || count === undefined);
    rows.push({
      value: option.value,
      label: option.label,
      count: counts === undefined ? undefined : count == null ? hiddenCount(minStudents).toLowerCase() : count.toLocaleString("en-US"),
      disabled: tooSmall && value !== option.value,
      selected: value === option.value,
    });
  }
  return rows;
}

/** A list of a filter's values, each a button with its student count; the picked one is marked. */
function OptionList({ label, rows, onPick }: { label: string; rows: OptionRow[]; onPick: (value: string | null) => void }) {
  return (
    <div role="group" aria-label={label} className="flex flex-col gap-0.5">
      {rows.map((row) => (
        <button
          key={row.value ?? "any"}
          type="button"
          aria-pressed={row.selected}
          disabled={row.disabled}
          onClick={() => onPick(row.value)}
          className={cn(
            "flex min-h-11 w-full cursor-pointer items-center justify-between gap-3 rounded-md px-2.5 text-left hover:bg-(--uncf-bg) disabled:cursor-not-allowed disabled:text-(--uncf-ink-3) disabled:hover:bg-transparent",
            row.selected && "bg-(--uncf-blue-tint) font-semibold hover:bg-(--uncf-blue-tint)",
          )}
        >
          <span>{row.label}</span>
          {row.count !== undefined && <span className="uncf-num text-[13px] whitespace-nowrap text-(--uncf-ink-3)">{row.count}</span>}
        </button>
      ))}
    </div>
  );
}

// The design's floating panel: white, a soft border and shadow, always light.
const panel = cn(
  explorerFontClass,
  "max-w-[calc(100vw-32px)] gap-0 rounded-[10px] border border-(--uncf-line-2) bg-(--uncf-surface) p-1.5 text-[15px] text-(--uncf-ink) shadow-[0_10px_28px_rgba(27,29,33,.14)] ring-0 [color-scheme:light]",
);
const panelHeading = "px-2.5 pt-2 pb-1 text-xs font-semibold tracking-[0.06em] text-(--uncf-ink-3) uppercase";

type SentencePickerProps = {
  definition: CohortFilterDefinition;
  value: string | null;
  counts?: ValueCounts;
  /** The API's min_students: values with fewer students have no count. Left out while loading. */
  minStudents?: number;
  onChange: (value: string | null) => void;
  disabled?: boolean;
};

/** A word in the cohort sentence ("first-time", "2023-24") that opens its filter's values. */
export function SentencePicker({ definition, value, counts, minStudents, onChange, disabled }: SentencePickerProps) {
  const [open, setOpen] = useState(false);
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        disabled={disabled}
        aria-label={`${definition.label}: ${filterValueLabel(definition, value)}`}
        className="group inline-flex min-h-10 cursor-pointer items-center gap-1 rounded-md px-1.5 font-semibold text-(--uncf-blue) underline decoration-dotted underline-offset-4 hover:bg-(--uncf-blue-tint) disabled:cursor-default data-popup-open:bg-(--uncf-blue-tint)"
      >
        {sentenceWord(definition, value)}
        <ChevronDown className="size-3.5 transition-transform group-data-popup-open:rotate-180 motion-reduce:transition-none" aria-hidden />
      </PopoverTrigger>
      <PopoverContent align="start" sideOffset={6} className={cn(panel, "w-72")}>
        <span className={panelHeading}>{definition.label}</span>
        <OptionList
          label={definition.label}
          rows={optionRows(definition, value, counts, minStudents)}
          onPick={(next) => {
            onChange(next);
            setOpen(false);
          }}
        />
        {definition.hint && <p className="px-2.5 pt-1 pb-1.5 text-[13px] text-(--uncf-ink-3)">{definition.hint}</p>}
      </PopoverContent>
    </Popover>
  );
}

type FilterPickerProps = {
  /** The "Add filter" filters, in the menu's order. */
  definitions: CohortFilterDefinition[];
  filters: CohortFilters;
  /** Students with each value, by filter id. Left out while they load. */
  counts?: Record<string, ValueCounts>;
  /** The API's min_students: values with fewer students have no count. Left out while loading. */
  minStudents?: number;
  onChange: (id: string, value: string | null) => void;
  /** Runs after a value is picked, e.g. to close the menu. */
  onPicked?: () => void;
  /** Where counts come from, for the note under a filter's values. */
  countsNote: string;
};

/** The "Add filter" list: groups of filters with their current values, then one filter's values. */
function FilterPicker({ definitions, filters, counts, minStudents, onChange, onPicked, countsNote }: FilterPickerProps) {
  const [picking, setPicking] = useState<string | null>(null);
  const current = definitions.find((definition) => definition.id === picking);

  if (current) {
    return (
      <div className="flex flex-col gap-0.5">
        <button type="button" onClick={() => setPicking(null)} className="flex min-h-10 cursor-pointer items-center gap-1.5 rounded-md px-2.5 text-sm text-(--uncf-blue) hover:bg-(--uncf-bg)">
          <ChevronLeft className="size-3.5" aria-hidden />
          All filters
        </button>
        <span className="px-2.5 pb-1 font-semibold">{current.label}</span>
        <OptionList
          label={current.label}
          rows={optionRows(current, filters[current.id] ?? null, counts?.[current.id], minStudents)}
          onPick={(value) => {
            onChange(current.id, value);
            setPicking(null);
            onPicked?.();
          }}
        />
        <p className="px-2.5 pt-1 pb-1.5 text-[13px] text-(--uncf-ink-3)">{countsNote}</p>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-0.5">
      {filterGroups.map((group) => (
        <div key={group} role="group" aria-label={group} className="flex flex-col gap-0.5">
          <span className={panelHeading}>{group}</span>
          {definitions
            .filter((definition) => definition.group === group)
            .map((definition) => {
              const value = filters[definition.id] ?? null;
              return (
                <button
                  key={definition.id}
                  type="button"
                  onClick={() => setPicking(definition.id)}
                  className="flex min-h-11 cursor-pointer items-center justify-between gap-3 rounded-md px-2.5 text-left hover:bg-(--uncf-bg)"
                >
                  <span>{definition.label}</span>
                  <span className={cn("inline-flex items-center gap-1.5 text-sm", value === null ? "text-(--uncf-ink-3)" : "font-semibold text-(--uncf-blue)")}>
                    {value === null ? "Any" : filterValueLabel(definition, value)}
                    <ChevronRight className="size-3.5" aria-hidden />
                  </span>
                </button>
              );
            })}
        </div>
      ))}
    </div>
  );
}

type AddFilterMenuProps = Omit<FilterPickerProps, "onPicked"> & { disabled?: boolean };

/** "+ Add filter": a menu of the filters by group, then the values of the one picked. */
export function AddFilterMenu({ disabled, ...picker }: AddFilterMenuProps) {
  const [open, setOpen] = useState(false);
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        disabled={disabled}
        className="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border border-(--uncf-blue) bg-(--uncf-surface) px-4 font-semibold text-(--uncf-blue) hover:bg-(--uncf-blue-tint) disabled:cursor-default data-popup-open:bg-(--uncf-blue-tint)"
      >
        <Plus className="size-4" aria-hidden />
        Add filter
      </PopoverTrigger>
      <PopoverContent align="end" sideOffset={6} className={cn(panel, "max-h-[min(470px,70vh)] w-85 overflow-y-auto")}>
        {/* Mounted only while open, so each time it opens it starts at the list of filters. */}
        {open && <FilterPicker {...picker} onPicked={() => setOpen(false)} />}
      </PopoverContent>
    </Popover>
  );
}

type FilterSheetProps = FilterPickerProps & {
  /** Who's shown, in words, under the title. */
  summary: string;
  /** The button that closes the sheet: "Show 351 students". */
  showLabel: string;
  activeCount: number;
  onClearAll: () => void;
  disabled?: boolean;
};

/** On a phone: one "Filters" button that opens every "Add filter" filter in a sheet from the bottom. */
export function FilterSheet({ summary, showLabel, activeCount, onClearAll, disabled, ...picker }: FilterSheetProps) {
  const [open, setOpen] = useState(false);
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger
        disabled={disabled}
        className="inline-flex min-h-11 flex-none cursor-pointer items-center gap-2 rounded-lg border border-(--uncf-blue) bg-(--uncf-surface) px-3.5 font-semibold whitespace-nowrap text-(--uncf-blue) disabled:cursor-default"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden>
          <path d="M2.5 4h11M4.5 8h7M6.5 12h3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
        </svg>
        {activeCount ? `Filters · ${activeCount}` : "Filters"}
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-50 bg-[rgba(27,29,33,.45)]" />
        <Dialog.Popup
          className={cn(
            explorerFontClass,
            "fixed inset-x-0 bottom-0 z-50 flex max-h-[86svh] flex-col rounded-t-2xl bg-(--uncf-surface) text-[15px] text-(--uncf-ink) shadow-[0_-8px_28px_rgba(27,29,33,.18)] [color-scheme:light]",
          )}
        >
          <div className="flex items-center justify-between pt-3.5 pr-3 pb-1 pl-4">
            <Dialog.Title className="text-[19px] font-semibold">Filters</Dialog.Title>
            <Dialog.Close aria-label="Close filters" className="inline-flex size-11 cursor-pointer items-center justify-center rounded-full text-(--uncf-ink-2)">
              <X className="size-4" aria-hidden />
            </Dialog.Close>
          </div>
          <Dialog.Description className="px-4 pb-1.5 text-(--uncf-ink-2)">{summary}</Dialog.Description>
          <div className="overflow-y-auto px-2">
            <FilterPicker {...picker} />
          </div>
          <div className="flex items-center justify-between gap-3 border-t border-(--uncf-line) px-4 pt-3 pb-6">
            <button type="button" className={explorerLinkButton} onClick={onClearAll}>
              Clear all
            </button>
            <Dialog.Close className={cn(explorerPrimaryButton, "min-h-12 px-5")}>{showLabel}</Dialog.Close>
          </div>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
