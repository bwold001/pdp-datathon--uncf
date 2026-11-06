/** Announces the caller's plain-language description of the filtered students. */
export function FilteredStudentsSummary({ children }: { children: React.ReactNode }) {
  return (
    <p role="status" className="text-sm text-muted-foreground">{children}</p>
  );
}
