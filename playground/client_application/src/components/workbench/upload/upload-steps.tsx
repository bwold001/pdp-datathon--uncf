import { Check } from "lucide-react";
import { cn } from "cn";

import { StepNumber } from "@/components/step-number";

type StepState = "done" | "current" | "upcoming";

type UploadStepsProps = {
  /** Step labels in order, such as "Choose files", "Check", "Save". */
  steps: string[];
  /** Index of the step in progress. Pass steps.length once every step is done. */
  currentStep: number;
  className?: string;
};

/** Steps before the current one are done; the current one is in progress; the rest are upcoming. */
function stepState(index: number, currentStep: number): StepState {
  if (index < currentStep) return "done";
  return index === currentStep ? "current" : "upcoming";
}

/** The upload page's numbered steps, with each step marked done, current or upcoming. */
export function UploadSteps({ steps, currentStep, className }: UploadStepsProps) {
  return (
    <ol aria-label="Upload steps" className={cn("flex flex-wrap gap-2", className)}>
      {steps.map((label, index) => {
        const state = stepState(index, currentStep);
        return (
          <li
            key={label}
            data-state={state}
            aria-current={state === "current" ? "step" : undefined}
            className={cn(
              "flex items-center gap-2 rounded-full py-1 pr-3 pl-1 text-sm",
              state === "current" && "bg-muted font-medium",
              state === "upcoming" && "text-muted-foreground",
            )}
          >
            <StepNumber size="sm" className={cn(state !== "upcoming" && "border-foreground")}>
              {state === "done" ? <Check aria-hidden className="size-3.5" /> : index + 1}
            </StepNumber>
            {label}
            {state === "done" && <span className="sr-only"> (done)</span>}
          </li>
        );
      })}
    </ol>
  );
}
