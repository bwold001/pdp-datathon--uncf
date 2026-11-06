import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

// Each markdown element as the app styles it. GitHub tables become the shared Table.
const components: Components = {
  p: ({ children }) => <p className="leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="ml-5 list-disc space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="ml-5 list-decimal space-y-1">{children}</ol>,
  h1: ({ children }) => <h3 className="font-semibold">{children}</h3>,
  h2: ({ children }) => <h3 className="font-semibold">{children}</h3>,
  h3: ({ children }) => <h4 className="font-medium">{children}</h4>,
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noreferrer" className="underline underline-offset-4">
      {children}
    </a>
  ),
  pre: ({ children }) => (
    <pre className="overflow-x-auto rounded-lg bg-muted p-3 font-mono text-xs [&_code]:bg-transparent [&_code]:p-0">
      {children}
    </pre>
  ),
  code: ({ children }) => <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]">{children}</code>,
  table: ({ children }) => (
    <div className="rounded-lg border">
      <Table>{children}</Table>
    </div>
  ),
  thead: ({ children }) => <TableHeader className="bg-muted/50">{children}</TableHeader>,
  tbody: ({ children }) => <TableBody>{children}</TableBody>,
  tr: ({ children }) => <TableRow>{children}</TableRow>,
  th: ({ children, style }) => <TableHead style={style}>{children}</TableHead>,
  td: ({ children, style }) => <TableCell style={style}>{children}</TableCell>,
};

/** Markdown from an LLM, with GitHub tables. Raw HTML in it is shown as text, never run. */
export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div className={cn("flex flex-col gap-3 text-sm", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}
