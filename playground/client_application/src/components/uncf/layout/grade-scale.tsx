import type { GradeScale as Scale } from "@/components/uncf/layout/explorer-api";

/** Which page's rule the table shows: what counts as a DFW, or what passes a gateway course. */
type GradeRule = "dfw" | "gateway";

const columns: Record<GradeRule, { title: string; yes: string; no: string }> = {
  dfw: { title: "Counts as a DFW?", yes: "Yes, a DFW", no: "No, passed" },
  gateway: { title: "Passes the course?", yes: "Yes, passed", no: "No, didn’t pass" },
};

/** The grade scale the numbers use, as a table under "How grades are counted": each grade's points and the page's rule. */
export function GradeScaleTable({ scale, rule }: { scale: Scale; rule: GradeRule }) {
  const column = columns[rule];
  return (
    <details className="group mt-3 rounded-md border border-(--uncf-line) bg-(--uncf-surface)">
      <summary className="cursor-pointer px-3.5 py-2.5 text-sm font-semibold text-(--uncf-ink)">How grades are counted</summary>
      <div className="border-t border-(--uncf-line) px-3.5 pt-2.5 pb-3.5">
        <p className="mb-2.5 text-[13px] text-(--uncf-ink-3)">
          The data has grade points (0 to 4) and a few codes, not letters. The groups below are cut only where the rule
          draws a line, so each grade point falls in exactly one group. A number between letters takes the letter below
          it: 1.5 is a D+, so it’s a D.
        </p>
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-(--uncf-line-2) text-[13px] text-(--uncf-ink-3)">
              <th scope="col" className="py-1.5 pr-3 font-semibold">Grade</th>
              <th scope="col" className="py-1.5 pr-3 font-semibold">Grade points</th>
              <th scope="col" className="py-1.5 font-semibold">{column.title}</th>
            </tr>
          </thead>
          <tbody>
            {scale.grades.map((row) => {
              const yes = row.counted;
              // The grades a page warns about stand out: a DFW, or a gateway grade that didn't pass.
              const warn = rule === "dfw" ? yes : !yes;
              return (
                <tr key={row.grade} className="border-b border-(--uncf-line) last:border-b-0">
                  <th scope="row" className="uncf-num py-1.5 pr-3 font-semibold">{row.grade}</th>
                  <td className="uncf-num py-1.5 pr-3 text-(--uncf-ink-2)">{row.points}</td>
                  <td className={warn ? "py-1.5 font-semibold text-(--uncf-orange-ink)" : "py-1.5 text-(--uncf-ink-2)"}>
                    {yes ? column.yes : column.no}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <p className="mt-2.5 text-[13px] text-(--uncf-ink-3)">Not counted: {scale.left_out}</p>
      </div>
    </details>
  );
}
