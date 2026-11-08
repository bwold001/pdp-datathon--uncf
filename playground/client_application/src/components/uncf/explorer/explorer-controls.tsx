"use client";

import { ChevronDown, Plus, X } from "lucide-react";

import { cohorts, dimensions, type Cohort, type Dimension } from "@/app/(app)/uncf/data";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";

import { cohortLabel, dimensionInfo } from "./labels";

export type DetailMode = "plain" | "analyst";

type ExplorerControlsProps = {
  cohort: Cohort;
  first: Dimension;
  second: Dimension | null;
  mode: DetailMode;
  onCohortChange: (cohort: Cohort) => void;
  onFirstChange: (dimension: Dimension) => void;
  onSecondChange: (dimension: Dimension | null) => void;
  onModeChange: (mode: DetailMode) => void;
};

/** One plain sentence holds the choices: "Show students by [Pell grant] and [start term] who entered in [2022–23]". */
export function ExplorerControls(props: ExplorerControlsProps) {
  const { cohort, first, second, mode, onCohortChange, onFirstChange, onSecondChange, onModeChange } = props;
  const secondOptions = dimensions.filter((dimension) => dimension !== first);

  return (
    <section aria-label="What to show" className="flex flex-col gap-4 rounded-2xl border bg-card p-5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
        <p className="flex flex-wrap items-baseline gap-x-2 gap-y-1 text-lg leading-relaxed font-medium tracking-tight text-muted-foreground sm:text-xl">
          <span>Show students by</span>
          <InlineSelect
            label="Group students by"
            value={first}
            options={dimensions.map((dimension) => ({ value: dimension, label: dimensionInfo[dimension].phrase }))}
            onChange={(value) => {
              onFirstChange(value);
              if (value === second) onSecondChange(null);
            }}
          />
          {second && (
            <>
              <span>and</span>
              <span className="inline-flex items-baseline gap-1">
                <InlineSelect
                  label="Then group by"
                  value={second}
                  options={secondOptions.map((dimension) => ({ value: dimension, label: dimensionInfo[dimension].phrase }))}
                  onChange={onSecondChange}
                />
                <button
                  type="button"
                  onClick={() => onSecondChange(null)}
                  aria-label="Remove the second grouping"
                  className="inline-flex size-8 items-center justify-center self-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
                >
                  <X className="size-4" aria-hidden />
                </button>
              </span>
            </>
          )}
          <span>who entered in</span>
          <InlineSelect
            label="Entering class"
            value={cohort}
            options={cohorts.map((value) => ({ value, label: cohortLabel(value) }))}
            onChange={onCohortChange}
          />
        </p>
        <ToggleGroup
          aria-label="Level of detail"
          multiple={false}
          value={[mode]}
          onValueChange={(values) => {
            const next = values[0];
            if (next === "plain" || next === "analyst") onModeChange(next);
          }}
          variant="outline"
        >
          <ToggleGroupItem value="plain" className={selectedToggle}>Plain language</ToggleGroupItem>
          <ToggleGroupItem value="analyst" className={selectedToggle}>Analyst</ToggleGroupItem>
        </ToggleGroup>
      </div>

      {!second && (
        <button
          type="button"
          onClick={() => onSecondChange(secondOptions[0])}
          className="inline-flex w-fit items-center gap-1.5 rounded-md text-sm font-medium text-indigo-700 underline-offset-4 hover:underline focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none dark:text-indigo-300"
        >
          <Plus className="size-4" aria-hidden />
          Add a second grouping
        </button>
      )}
    </section>
  );
}

/** The selected option stands out by more than a light tint, so it reads in grayscale and at 3:1. */
export const selectedToggle = "aria-pressed:bg-foreground aria-pressed:text-background data-[pressed]:bg-foreground data-[pressed]:text-background";

type InlineSelectProps<Value extends string> = {
  label: string;
  value: Value;
  options: { value: Value; label: string }[];
  onChange: (value: Value) => void;
};

/** A native select that reads as part of the sentence and sizes itself to the chosen option. */
function InlineSelect<Value extends string>({ label, value, options, onChange }: InlineSelectProps<Value>) {
  return (
    <span className="relative inline-flex items-center">
      <select
        aria-label={label}
        value={value}
        onChange={(event) => onChange(event.target.value as Value)}
        className={cn(
          "cursor-pointer appearance-none rounded-none border-0 border-b-2 border-indigo-600 bg-transparent py-0 pr-7 pl-0.5 font-semibold text-indigo-700 outline-none [field-sizing:content]",
          "focus-visible:rounded-sm focus-visible:ring-[3px] focus-visible:ring-ring/50 dark:border-indigo-400 dark:text-indigo-300",
        )}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-1 size-4 text-indigo-600 dark:text-indigo-400" aria-hidden />
    </span>
  );
}
