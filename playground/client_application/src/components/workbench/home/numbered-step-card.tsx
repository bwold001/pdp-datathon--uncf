import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StepNumber } from "@/components/step-number";

type NumberedStepCardProps = {
  step: number;
  title: string;
  /** One short line on what happens in this step. */
  children: React.ReactNode;
};

/**
 * One step of a short how-it-works row. Place inside an `<li>` of an `<ol>`. Its title is an h3, under a
 * page section heading.
 */
export function NumberedStepCard({ step, title, children }: NumberedStepCardProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex flex-col gap-3">
        <StepNumber>{step}</StepNumber>
        <CardTitle>
          <h3>{title}</h3>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{children}</p>
      </CardContent>
    </Card>
  );
}
