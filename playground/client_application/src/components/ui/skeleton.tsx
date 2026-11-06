import { cn } from "cn";

/** Grey placeholder shown while content loads. Pulses unless the visitor prefers reduced motion. */
export function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return <div aria-hidden className={cn("rounded bg-muted motion-safe:animate-pulse", className)} {...props} />;
}
