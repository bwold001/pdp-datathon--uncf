import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export type ComparisonStatCardProps = { label: string } & (
  | { kind: "count"; value: number; total: number }
  | { kind: "rate"; value: number | null; baseline: number | null }
);

/** Shows a caller-supplied count or rate alongside its all-student baseline. */
export function ComparisonStatCard(props: ComparisonStatCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <h3>{props.label}</h3>
        </CardTitle>
        <CardDescription>{props.kind === "rate" ? "Students with a reported value" : "Students matching"}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="text-3xl font-semibold tabular-nums">
          {props.value === null ? "—" : `${props.value.toLocaleString("en-US")}${props.kind === "rate" ? "%" : ""}`}
        </p>
        {props.kind === "rate" ? (
          <>
            {props.value !== null && (
              <div className="relative py-1">
                <Progress value={props.value} aria-label={`${props.label}: matching students`} />
                {props.baseline !== null && (
                  <span aria-hidden className="absolute inset-y-0 w-0.5 bg-foreground" style={{ left: `clamp(0px, ${props.baseline}%, calc(100% - 2px))` }} />
                )}
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              {props.baseline === null ? "All students: no reported values" : `All students ${props.baseline.toLocaleString("en-US")}%`}
            </p>
            {props.value === null && <p className="text-sm text-muted-foreground">No reported values in this group</p>}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">of {props.total.toLocaleString("en-US")} students</p>
        )}
      </CardContent>
    </Card>
  );
}
