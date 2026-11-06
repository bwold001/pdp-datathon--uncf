import Link from "next/link";
import { ArrowRight } from "lucide-react";

export type StarterQuestion = { question: string; filterHint: string; href: string };

/** Links to example questions using destinations supplied by the caller. */
export function StarterQuestionList({ questions }: { questions: StarterQuestion[] }) {
  return (
    <ul className="flex flex-col gap-2">
      {questions.map(({ question, filterHint, href }) => (
        <li key={href}>
          <Link href={href} className="flex items-center justify-between gap-4 rounded-full border px-5 py-3 outline-none hover:bg-muted focus-visible:ring-3 focus-visible:ring-ring/50">
            <span>{question}</span>
            <span className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
              {filterHint}
              <ArrowRight aria-hidden className="size-3.5" />
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
