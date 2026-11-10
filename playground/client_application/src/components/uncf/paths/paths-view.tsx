import {
  Card,
  CardHead,
  Counted,
  Kpi,
  KpiGrid,
  Legend,
  MessageCard,
  Notice,
  TrackBar,
  TwoColumns,
  formatCount,
  formatShare,
  shareOf,
  tableClasses,
} from "@/components/uncf/layout/explorer-parts";
import { cn } from "@/lib/utils";

import { type PathsResponse, pathStatuses, statusStyle, termNames } from "./paths-data";
import { PathsSankey } from "./paths-sankey";

/** The Student paths tab drawn from the API's answer: tiles, the student flow, transfers and the term table. */
export function PathsView({ data }: { data: PathsResponse }) {
  if (data.status === "suppressed" || !data.students || !data.columns || !data.transfers) {
    return (
      <MessageCard title="Fewer than 10 students match these filters.">
        Remove a filter to see results. Groups under 10 students are hidden to protect privacy.
      </MessageCard>
    );
  }
  const names = termNames(data);
  const total = data.students;
  const year2 = data.columns.year2;
  const returned = data.moves?.find((move) => move.from === "stopped" && move.to === "here")?.students ?? null;
  const notObserved = data.columns.next.not_observed || data.columns.year2.not_observed;

  return (
    <>
      {data.meta.provisional && (
        <Notice title={`The ${data.meta.cohort} class’s second year is still arriving.`}>
          Later terms are only partly in this PDP submission, so they show fewer students enrolled than the final count
          will.
        </Notice>
      )}
      <KpiGrid columns={4}>
        <Kpi
          label="Entering cohort"
          value={total.toLocaleString("en-US")}
          note={`First-time, ${names.entered ?? data.meta.cohort}`}
        />
        {/* These two count one term from course records, not PDP retention or persistence (year-2 flags, defined in
            Key terms), so they name what they count. */}
        <Kpi
          label={`Still here · ${names.year2Short}`}
          value={formatShare(shareOf(year2.here, total))}
          tone="blue"
          note={`${formatCount(year2.here)} took a course here that term`}
        />
        <Kpi
          label={`Enrolled anywhere · ${names.year2Short}`}
          value={formatShare(shareOf(year2.anywhere, total))}
          note={`Here or at another college in ${names.year2Short}`}
        />
        <Kpi
          label={`Stopped out by ${names.year2Short}`}
          value={formatShare(shareOf(year2.stopped, total))}
          tone="warn"
          note={returnedNote(returned)}
        />
      </KpiGrid>

      <Card>
        <CardHead
          title="Student flow, term by term"
          aside={<Legend items={pathStatuses.map((status) => ({ label: statusStyle[status].label, color: statusStyle[status].node }))} />}
        />
        <div className="overflow-x-auto">
          <PathsSankey data={data} />
        </div>
        {notObserved ? (
          <p className="mt-3 text-[13px] text-(--uncf-ink-3)">
            {formatCount(notObserved)} students’ later terms aren’t in the data yet, so they aren’t drawn there.
          </p>
        ) : null}
        <Counted>
          first-time students in the entering cohort, by their record each term in the PDP course file. Enrolled here:
          took a course here that term. Transferred out: no course here, but the file records enrollment at another
          college that term. Stopped out: no record that term. These come from term records, so they can differ from the
          cohort file’s retention and persistence flags. Hover a band to see its count.
        </Counted>
      </Card>

      <TwoColumns>
        <TransfersCard data={data} year2={names.year2} />
        <TermTableCard data={data} />
      </TwoColumns>
    </>
  );
}

/** The stopped-out tile's note: how many came back after a term with no record. */
function returnedNote(returned: number | null): string {
  if (returned === null) return "Under 10 students returned after a term away";
  if (returned === 0) return "No students returned after a term away";
  return `${returned.toLocaleString("en-US")} students returned after a term away`;
}

/** Of the students at another college in the last term, how many went to a 4-year or a 2-year college. */
function TransfersCard({ data, year2 }: { data: PathsResponse; year2: string }) {
  const transfers = data.transfers!;
  const moved = transfers.students;
  const rows = [
    { label: "To a 4-year institution", count: transfers.four_year },
    { label: "To a 2-year institution", count: transfers.two_year },
    // Shown only when there are some: a mix of college types, or a type the file leaves blank.
    ...(transfers.other === 0 ? [] : [{ label: "Other, mixed or not recorded", count: transfers.other }]),
  ];

  return (
    <Card>
      <h3 className="text-[21px] font-semibold">Where transfers went</h3>
      <p className="mt-1 text-(--uncf-ink-3)">
        {moved === null
          ? `Fewer than 10 students transferred out by ${year2}, so this is hidden.`
          : moved === 0
            ? `No students transferred out by ${year2}.`
            : `Of ${moved.toLocaleString("en-US")} students who transferred out by ${year2}`}
      </p>
      {moved ? (
        <>
          <div className="mt-5 flex flex-col gap-5.5">
            {rows.map((row) => {
              const share = shareOf(row.count, moved);
              return (
                <div key={row.label} className="flex flex-col gap-1.5">
                  <div className="flex justify-between gap-3">
                    <span>{row.label}</span>
                    <span className="uncf-num">
                      {formatCount(row.count)}
                      {share !== null && ` · ${formatShare(share)}`}
                    </span>
                  </div>
                  <TrackBar share={share} color="var(--uncf-grey)" label={`${row.label}: ${formatCount(row.count)}`} />
                </div>
              );
            })}
          </div>
          <p className="mt-4 text-[13px] text-(--uncf-ink-3)">College type is the other college’s Carnegie class in the course file.</p>
        </>
      ) : null}
    </Card>
  );
}

/** Each term's counts as a table: the flow chart's numbers in rows. */
function TermTableCard({ data }: { data: PathsResponse }) {
  const names = termNames(data);
  const columns = data.columns!;
  const rows = [
    { term: names.entered ?? "Entering term", here: formatCount(data.students), elsewhere: "–", stopped: "–" },
    { term: capitalize(names.next), here: formatCount(columns.next.here), elsewhere: formatCount(columns.next.elsewhere), stopped: formatCount(columns.next.stopped) },
    { term: capitalize(names.year2), here: formatCount(columns.year2.here), elsewhere: formatCount(columns.year2.elsewhere), stopped: formatCount(columns.year2.stopped) },
  ];

  return (
    <Card>
      <h3 className="mb-4 text-[21px] font-semibold">Term-by-term table</h3>
      <div className="overflow-x-auto">
        <table className={tableClasses.table}>
          <thead>
            <tr>
              <th className={tableClasses.th}>Term</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Enrolled</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Transferred</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Stopped out</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.term}>
                <td className={tableClasses.td}>{row.term}</td>
                <td className={cn(tableClasses.td, tableClasses.right, "uncf-num")}>{row.here}</td>
                <td className={cn(tableClasses.td, tableClasses.right, "uncf-num")}>{row.elsewhere}</td>
                <td className={cn(tableClasses.td, tableClasses.right, "uncf-num")}>{row.stopped}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

/** The text with its first letter in capitals. */
function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
