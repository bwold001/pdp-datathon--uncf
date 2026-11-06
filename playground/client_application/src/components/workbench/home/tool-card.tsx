import Link from "next/link";
import { cn } from "cn";

import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type ToolCardProps = {
  name: string;
  description: string;
  /** A short label above the name, such as "Example", "Needs data" or "Your team". */
  tag: string;
  /** The team tool's own page. */
  href: string;
  /** "add" is the dashed card that invites a team to add its own tool. */
  variant?: "default" | "add";
};

/**
 * One team tool in Home's Team tools section. Its name link stretches across the card. Its title is an h3,
 * under the section's h2. Place inside an `<li>`.
 */
export function ToolCard({ name, description, tag, href, variant = "default" }: ToolCardProps) {
  return (
    <Card
      className={cn(
        "relative h-full transition-colors hover:bg-muted has-[a:focus-visible]:ring-3 has-[a:focus-visible]:ring-ring/50",
        variant === "add" && "border-2 border-dashed bg-transparent ring-0",
      )}
    >
      <CardHeader className="flex flex-col gap-2">
        <Badge variant={variant === "add" ? "outline" : "secondary"}>{tag}</Badge>
        <CardTitle>
          <h3>
            <Link href={href} data-variant={variant} className="outline-none after:absolute after:inset-0">
              {name}
            </Link>
          </h3>
        </CardTitle>
        <CardDescription>
          <p>{description}</p>
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
