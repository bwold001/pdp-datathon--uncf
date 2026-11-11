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
import { hiddenCount, privacyNote, tooFew } from "@/components/uncf/layout/small-groups";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

import {
  type FocusCounts,
  type PathFocus,
  type PathStatus,
  type PathsResponse,
  focusCounts,
  focusPhrase,
  pathStatuses,
  statusStyle,
  studentsLabel,
  termNames,
} from "./paths-data";
import { PathsSankey } from "./paths-sankey";

type PathsViewProps = {
  data: PathsResponse;
  /** The students clicked in the flow, or null for the whole cohort. */
  focus?: PathFocus | null;
  /** Called when someone clicks a band or bar, or clears the focus. Without it, the flow isn't clickable. */
  onFocusChange?: (focus: PathFocus | null) => void;
};

/**
 * The Student paths tab drawn from the API's answer: tiles, the student flow, transfers and the term table. With a
 * focus, the tiles and the table count only the students in the band or bar someone clicked.
 */
export function PathsView({ data, focus = null, onFocusChange }: PathsViewProps) {
  if (data.status === "suppressed" || !data.students || !data.columns || !data.transfers) {
    return (
      <MessageCard title={`${tooFew(data.meta.min_students)} match these filters.`}>
        Remove a filter to see results. {privacyNote(data.meta.min_students)}
      </MessageCard>
    );
  }
  const names = termNames(data);
  const total = data.students;
  const focused = focus ? focusCounts(data, focus) : null;
  const year2 = data.columns.year2;
  const returned = focused ? focused.returned : (data.moves?.find((move) => move.from === "stopped" && move.to === "here")?.students ?? null);
  const notObserved = data.columns.next.not_observed || data.columns.year2.not_observed;
  // A focused tile's share is of the focused students; otherwise the API's share of everyone who entered.
  const share = (status: "here" | "stopped") => (focused ? shareOf(focused.year2[status], focused.students) : year2.shares[status]);
  const count = (status: "here" | "stopped") => (focused ? focused.year2[status] : year2[status]);

  return (
    <>
      {focus && focused && onFocusChange && (
        <FocusBar phrase={focusPhrase(data, focus)} students={focused.students} total={total} minStudents={data.meta.min_students} onClear={() => onFocusChange(null)} />
      )}
      {data.meta.provisional && (
        <Notice title={`The ${data.meta.cohort} class’s second year is still arriving.`}>
          Later terms are only partly in this PDP submission, so they show fewer students enrolled than the final count
          will.
        </Notice>
      )}
      <KpiGrid columns={4}>
        {focused ? (
          <Kpi
            label="Students in focus"
            value={formatCount(focused.students, data.meta.min_students)}
            note={`${formatShare(shareOf(focused.students, total))} of the ${total.toLocaleString("en-US")} who entered`}
          />
        ) : (
          <Kpi
            label="Entering cohort"
            value={total.toLocaleString("en-US")}
            note={`${studentsLabel(data)}, ${names.entered ?? data.meta.cohort}`}
          />
        )}
        {/* These two count one term from course records, not PDP retention or persistence (year-2 flags, defined in
            Key terms), so they name what they count. */}
        <Kpi
          label={`Still here · ${names.year2Short}`}
          value={formatShare(share("here"))}
          tone="blue"
          note={`${formatCount(count("here"), data.meta.min_students)} took a course here that term`}
        />
        <Kpi
          label={`Enrolled anywhere · ${names.year2Short}`}
          value={formatShare(focused ? shareOf(anywhere(focused), focused.students) : year2.shares.anywhere)}
          note={`Here or at another college in ${names.year2Short}`}
        />
        <Kpi
          label={`Stopped out by ${names.year2Short}`}
          value={formatShare(share("stopped"))}
          tone="warn"
          note={returnedNote(returned, data.meta.min_students)}
        />
      </KpiGrid>

      <Card>
        <CardHead
          title="Student flow, term by term"
          aside={<Legend items={pathStatuses.map((status) => ({ label: statusStyle[status].label, color: statusStyle[status].node }))} />}
        />
        <div className="overflow-x-auto">
          <PathsSankey data={data} focus={focus} onFocusChange={onFocusChange} />
        </div>
        {notObserved ? (
          <p className="mt-3 text-[13px] text-(--uncf-ink-3)">
            {formatCount(notObserved, data.meta.min_students)} students’ later terms aren’t in the data yet, so they aren’t drawn there.
          </p>
        ) : null}
        <Counted>
          the entering cohort’s students the cohort bar picks (first-time unless Enrollment type says otherwise), by their
          record each term in the PDP course file. Enrolled here: took a course here that term. Earned a credential: no
          course here, but earned a credential here in an earlier year. Transferred out: neither, but the file records
          enrollment at another college that term. Stopped out: no record that term. These come from term records, so
          they can differ from the cohort file’s retention and persistence flags. Hover a band to see its count
          {onFocusChange ? "; click a band or bar to highlight it and count only its students in the tiles." : "."}
        </Counted>
      </Card>

      <TwoColumns>
        <TransfersCard data={data} year2={names.year2} />
        <TermTableCard data={data} focus={focus} />
      </TwoColumns>
    </>
  );
}

type FocusBarProps = { phrase: string; students: number | null; total: number; minStudents: number; onClear: () => void };

/** Says which students the tiles and table count once someone clicks the flow, with a way back to everyone. */
function FocusBar({ phrase, students, total, minStudents, onClear }: FocusBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-2" role="status">
      <span className="text-sm font-medium text-(--uncf-ink-2)">Focused on</span>
      <span className="inline-flex items-center gap-1 rounded-full border border-(--uncf-ink-3) bg-(--uncf-surface) py-1 pr-1 pl-3.5 font-medium">
        {phrase} · <span className="uncf-num">{formatCount(students, minStudents)}</span>
        <button
          type="button"
          data-pdf-skip
          onClick={onClear}
          aria-label="Show every student"
          className="ml-1 inline-flex size-6 cursor-pointer items-center justify-center rounded-full text-(--uncf-ink-3) hover:bg-(--uncf-band) hover:text-(--uncf-ink)"
        >
          <X className="size-4" aria-hidden />
        </button>
      </span>
      <span className="text-sm text-(--uncf-ink-3)">
        of {total.toLocaleString("en-US")} who entered. The tiles count only them.
        <span data-pdf-skip> Click it again or press Esc to show everyone.</span>
      </span>
    </div>
  );
}

/** Enrolled here or at another college in the third term: null when either count is hidden. */
function anywhere(focused: FocusCounts): number | null {
  const { here, elsewhere } = focused.year2;
  return here === null || elsewhere === null ? null : here + elsewhere;
}

/** The stopped-out tile's note: how many came back after a term with no record. */
function returnedNote(returned: number | null, minStudents: number): string {
  if (returned === null) return `${hiddenCount(minStudents)} students returned after a term away`;
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
          ? `${tooFew(data.meta.min_students)} transferred out by ${year2}, so this is hidden.`
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
                      {formatCount(row.count, data.meta.min_students)}
                      {share !== null && ` · ${formatShare(share)}`}
                    </span>
                  </div>
                  <TrackBar share={share} color="var(--uncf-grey)" label={`${row.label}: ${formatCount(row.count, data.meta.min_students)}`} />
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

/**
 * Each term's counts as a table: the flow chart's numbers in rows, for the whole cohort. With a focus, the cells of the
 * statuses clicked in the flow are highlighted in their color.
 */
function TermTableCard({ data, focus }: { data: PathsResponse; focus: PathFocus | null }) {
  const names = termNames(data);
  const columns = data.columns!;
  const rows = [
    { term: names.entered ?? "Entering term", here: formatCount(data.students, data.meta.min_students), credential: "–", elsewhere: "–", stopped: "–", picked: null },
    ...[
      { term: names.next, counts: columns.next, picked: focus?.next ?? null },
      { term: names.year2, counts: columns.year2, picked: focus?.year2 ?? null },
    ].map(({ term, counts, picked }) => ({
      term: capitalize(term),
      here: formatCount(counts.here, data.meta.min_students),
      credential: formatCount(counts.credential, data.meta.min_students),
      elsewhere: formatCount(counts.elsewhere, data.meta.min_students),
      stopped: formatCount(counts.stopped, data.meta.min_students),
      picked,
    })),
  ];
  /** A number cell, tinted in its status's color when it's the one clicked in the flow. */
  const cell = (status: PathStatus, picked: PathStatus | null, text: string) => (
    <td
      className={cn(tableClasses.td, tableClasses.right, "uncf-num", status === picked && "px-2 font-semibold")}
      style={status === picked ? { background: statusStyle[status].band } : undefined}
    >
      {text}
    </td>
  );

  return (
    <Card>
      <h3 className="mb-4 text-[21px] font-semibold">Term-by-term table</h3>
      <div className="overflow-x-auto">
        <table className={tableClasses.table}>
          <thead>
            <tr>
              <th className={tableClasses.th}>Term</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Enrolled</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Credential</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Transferred</th>
              <th className={cn(tableClasses.th, tableClasses.right)}>Stopped out</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.term}>
                <td className={tableClasses.td}>{row.term}</td>
                {cell("here", row.picked, row.here)}
                {cell("credential", row.picked, row.credential)}
                {cell("elsewhere", row.picked, row.elsewhere)}
                {cell("stopped", row.picked, row.stopped)}
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
