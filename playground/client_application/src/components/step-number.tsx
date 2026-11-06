import { cn } from "cn";

type StepNumberProps = {
  children: React.ReactNode;
  /** "sm" sits beside a line of text; "default" heads a card. */
  size?: "default" | "sm";
  className?: string;
};

/** A step's number in a circle, as in BuildSteps and the workbench NumberedStepCard. */
export function StepNumber({ children, size = "default", className }: StepNumberProps) {
  return (
    <span
      aria-hidden="true"
      data-slot="step-number"
      data-size={size}
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full border font-medium tabular-nums",
        size === "sm" ? "size-6 text-xs" : "size-9 text-sm",
        className,
      )}
    >
      {children}
    </span>
  );
}
