import { Card, CardHead, Kpi, KpiGrid, Legend, LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { explorerButton } from "@/components/uncf/layout/explorer-styles";
import { hidesSmallGroups } from "@/components/uncf/layout/small-groups";
import { cn } from "@/lib/utils";

import {
  type DfwCourseDetail,
  type DfwCourseSummary,
  type DfwSort,
  type DfwSplit,
  type DfwTally,
  dfShare,
  dfwDimensions,
  groupRows,
  minimumGrades,
  percent,
  sortHints,
} from "./dfw-data";

const fmt = (n: number) => n.toLocaleString("en-US");
const legend = [
  { label: "D or F", color: "var(--uncf-f)" },
  { label: "W", color: "var(--uncf-grey)" },
];

/** The three tiles: the DFW rate, then D-or-F and W as shares of all final grades. */
export function DfwKpis({ everyone }: { everyone: DfwTally }) {
  const split = everyone.split!;
  return (
    <KpiGrid columns={3}>
      <Kpi
        label="DFW rate"
        value={percent(everyone.rate)}
        tone="warn"
        note={`${fmt(everyone.num!)} of ${fmt(everyone.den!)} final grades were a D, F or W`}
      />
      <Kpi label="D or F" value={percent(dfShare(split))} note={`${fmt(split.DF)} final grades below a C`} />
      <Kpi label="Withdrew" value={percent(split.shares.W)} note={`${fmt(split.W)} withdrawals`} />
    </KpiGrid>
  );
}

/** D-or-F and W as parts of a course's final grades, on a grey track. */
function DfwBar({ split }: { split: DfwSplit | null }) {
  const width = (share: number) => `${share * 100}%`;
  return (
    <div className="flex h-3 overflow-hidden rounded-[3px] bg-(--uncf-track)" aria-hidden>
      {split && (
        <>
          <div style={{ width: width(dfShare(split)), background: "var(--uncf-f)" }} />
          <div style={{ width: width(split.shares.W), background: "var(--uncf-grey)" }} />
        </>
      )}
    </div>
  );
}

// The list's columns: course, final grades, the D/F-and-W bar, and the rate.
const rowGrid = "grid grid-cols-[minmax(0,1fr)_80px] items-center gap-3 sm:grid-cols-[minmax(0,1.6fr)_74px_minmax(90px,1.2fr)_92px]";

type CourseListProps = {
  courses: DfwCourseSummary[];
  /** Courses that pass the size cutoff, before "Show more". */
  total: number;
  sort: DfwSort;
  minimum: number;
  selected: string | null;
  onSelect: (course: string) => void;
  onSort: (sort: DfwSort) => void;
  onMinimum: (minimum: number) => void;
  onMore?: () => void;
};

/** The ranked course list, with the ranking and size controls. */
export function CourseList({ courses, total, sort, minimum, selected, onSelect, onSort, onMinimum, onMore }: CourseListProps) {
  return (
    <Card>
      <CardHead
        className="mb-3.5"
        title="Courses with the most D, F and W grades"
        subtitle={`Showing ${Math.min(courses.length, total)} of ${fmt(total)} courses with at least ${minimum} final grades`}
        aside={<Legend items={legend} />}
      />
      <div data-pdf-skip className="mb-4 flex flex-wrap items-center gap-x-5 gap-y-3 text-sm text-(--uncf-ink-2)">
        <span>Rank by</span>
        <div role="group" aria-label="Rank courses by" className="inline-flex overflow-hidden rounded-md border border-(--uncf-line-2)">
          {(["count", "rate"] as const).map((option) => (
            <button
              key={option}
              type="button"
              aria-pressed={sort === option}
              onClick={() => onSort(option)}
              className="cursor-pointer bg-(--uncf-surface) px-3 py-1.75 text-sm text-(--uncf-ink-2) not-first:border-l not-first:border-(--uncf-line-2) aria-pressed:bg-(--uncf-blue-tint) aria-pressed:font-semibold aria-pressed:text-(--uncf-blue)"
            >
              {option === "count" ? "Number of DFW grades" : "DFW rate"}
            </button>
          ))}
        </div>
        <label className="inline-flex items-center gap-2">
          Only courses with at least
          <select
            value={minimum}
            onChange={(event) => onMinimum(Number(event.target.value))}
            className="rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-2.5 py-1.75"
          >
            {minimumGrades.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          final grades
        </label>
      </div>
      <p className="-mt-1 mb-3.5 text-[13px] text-(--uncf-ink-3)">{sortHints[sort]}</p>
      <div className={cn(rowGrid, "hidden border-b border-(--uncf-line-2) px-2.5 pb-2 text-[13px] font-semibold text-(--uncf-ink-3) sm:grid")}>
        <span>Course</span>
        <span className="text-right">Final grades</span>
        <span>Share D or F · W</span>
        <span className="text-right">DFW rate</span>
      </div>
      {courses.length === 0 ? (
        <p className="px-2.5 py-4 text-[13px] text-(--uncf-ink-3)">No courses match. Lower the size cutoff.</p>
      ) : (
        <ul>
          {courses.map((course, index) => (
            <li key={course.course}>
              <button
                type="button"
                aria-pressed={course.course === selected}
                onClick={() => onSelect(course.course)}
                className={cn(
                  rowGrid,
                  "w-full cursor-pointer border-b border-(--uncf-line) px-2.5 py-2.75 text-left hover:bg-(--uncf-bg) aria-pressed:bg-(--uncf-blue-tint) aria-pressed:shadow-[inset_3px_0_0_var(--uncf-blue)]",
                )}
              >
                <span className="min-w-0">
                  <span className="uncf-num text-sm font-semibold">
                    <span className="mr-2 font-normal text-(--uncf-ink-3)">{index + 1}</span>
                    {course.course}
                  </span>
                  <span className="block truncate text-[13px] text-(--uncf-ink-3)">{course.names.top[0] ?? ""}</span>
                </span>
                <span className="uncf-num hidden text-right sm:block">{fmt(course.den)}</span>
                <span className="col-span-full row-start-2 sm:col-span-1 sm:row-start-auto">
                  <DfwBar split={course.split} />
                </span>
                <span className="text-right">
                  <b className="uncf-num font-medium">{percent(course.rate)}</b>
                  <small className="block text-xs text-(--uncf-ink-3)">{fmt(course.num)} DFW grades</small>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {onMore && (
        <button type="button" data-pdf-skip className={cn(explorerButton, "mt-3.5")} onClick={onMore}>
          Show 10 more
        </button>
      )}
    </Card>
  );
}

type CourseDetailProps = {
  detail: DfwCourseDetail;
  dimension: string;
  onDimension: (dimension: string) => void;
};

/** The selected course: its rate and split, then each group in it next to everyone else in the course. */
export function CourseDetail({ detail, dimension, onDimension }: CourseDetailProps) {
  const rows = groupRows(detail, dimension);
  const shown = rows.filter((row) => row.rate !== null).sort((a, b) => (b.gap ?? -999) - (a.gap ?? -999));
  const hidden = rows.filter((row) => row.rate === null);
  const min = detail.meta.min_students;
  const more = detail.names.distinct - detail.names.top.length;

  return (
    <DetailFrame>
      <div>
        <div className="mb-1.5 text-xs font-bold tracking-widest text-(--uncf-ink-2) uppercase">Selected course</div>
        <h3 className="uncf-num text-[21px] font-semibold">{detail.course}</h3>
        <p className="mt-1 text-(--uncf-ink-3)">
          {detail.names.top.length
            ? `Listed in the catalog as ${detail.names.top.join(" · ")}${more > 0 ? ` and ${more} more` : ""}`
            : "No course name in the data"}
        </p>
      </div>
      <div>
        <div className="uncf-num text-[40px] leading-[1.1] font-medium text-(--uncf-orange-ink)">{percent(detail.rate)}</div>
        <div className="text-[13px] text-(--uncf-ink-3)">
          {fmt(detail.num!)} of {fmt(detail.den!)} final grades were a D, F or W
        </div>
      </div>
      {detail.split && (
        <div>
          <DfwBar split={detail.split} />
          <div className="mt-2 flex flex-wrap gap-4 text-sm text-(--uncf-ink-2)">
            <span>D or F: {fmt(detail.split.DF)}</span>
            <span>W: {fmt(detail.split.W)}</span>
          </div>
        </div>
      )}
      <div className="flex flex-col gap-3.5 border-t border-(--uncf-line) pt-4">
        <div>
          <h3 className="text-[17px] font-semibold">Each group vs. everyone else in {detail.course}</h3>
          <p className="mt-0.5 text-[13px] text-(--uncf-ink-3)">
            The bar is the group’s DFW rate. The black line is the rate for all other students in this course. Groups
            furthest above everyone else come first.
          </p>
        </div>
        {/* Left out of a PDF: the rows below name their groups. */}
        <div role="group" aria-label="Compare by" data-pdf-skip className="flex flex-wrap gap-1.5">
          {dfwDimensions.map((option) => (
            <button
              key={option.id}
              type="button"
              aria-pressed={option.id === dimension}
              onClick={() => onDimension(option.id)}
              className="cursor-pointer rounded-full border border-(--uncf-line-2) bg-(--uncf-surface) px-3 py-1.25 text-[13px] text-(--uncf-ink-2) aria-pressed:border-(--uncf-ink) aria-pressed:bg-(--uncf-ink) aria-pressed:text-(--uncf-surface)"
            >
              {option.label}
            </button>
          ))}
        </div>
        <div className="flex flex-col gap-3">
          {shown.map((row) => (
            <div key={row.label}>
              <div className="flex justify-between gap-3 text-sm">
                <span className="min-w-0">
                  {row.label} <span className="text-(--uncf-ink-3)">· {fmt(row.grades!)} grades</span>
                </span>
                <span className="uncf-num">{percent(row.rate)}</span>
              </div>
              <div className="relative mt-1 h-3 rounded-[3px] bg-(--uncf-track)">
                <div className="h-full rounded-[3px] bg-(--uncf-blue)" style={{ width: `${row.rate! * 100}%` }} />
                {row.rest !== null && (
                  <span className="absolute -top-1 -bottom-1 w-0.5 bg-(--uncf-ink)" style={{ left: `${row.rest * 100}%` }} aria-hidden />
                )}
              </div>
              <div className="mt-1 text-[13px] text-(--uncf-ink-3)">{gapText(row.gap, row.rest)}</div>
            </div>
          ))}
          {shown.length === 0 && (
            <p className="text-[13px] text-(--uncf-ink-3)">No group in this course has {min} or more students.</p>
          )}
          {hidden.length > 0 && (
            <p className="text-[13px] text-(--uncf-ink-3)">
              {hidesSmallGroups(min) ? `Hidden to protect privacy (under ${min} students)` : "No students with final grades"}:{" "}
              {hidden.map((row) => row.label).join(", ")}
            </p>
          )}
        </div>
      </div>
    </DetailFrame>
  );
}

/** How a group compares with everyone else, in the design's words. */
function gapText(gap: number | null, rest: number | null): React.ReactNode {
  if (gap === null || rest === null) return "Too few other students to compare";
  if (Math.abs(gap) < 0.05) return `Same as everyone else (${percent(rest)})`;
  return (
    <>
      <span className={gap > 0 ? "font-semibold text-(--uncf-orange-ink)" : "font-semibold text-(--uncf-blue)"}>
        {gap > 0 ? "+" : "−"}
        {Math.abs(gap).toFixed(1)} pts
      </span>{" "}
      vs. everyone else ({percent(rest)})
    </>
  );
}

/** The detail card: it stays in view beside the list on a wide screen. */
export function DetailFrame({ children }: { children: React.ReactNode }) {
  return (
    <section aria-live="polite" className="min-[961px]:sticky min-[961px]:top-4">
      <Card className="flex flex-col gap-4.5">{children}</Card>
    </section>
  );
}

/** The detail card while the selected course loads. */
export function CourseDetailLoading() {
  return (
    <DetailFrame>
      <LoadingBlock className="h-16" />
      <LoadingBlock className="h-24" />
      <LoadingBlock className="h-64" />
    </DetailFrame>
  );
}

/** The detail card when the selected course couldn't load. */
export function CourseDetailError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <MessageCard title="This course couldn’t load." onRetry={onRetry}>
      {message}
    </MessageCard>
  );
}

/** The note under the page: what the numbers mean, in the design's words. minStudents is the answer's meta.min_students. */
export function DfwCounted({ minStudents }: { minStudents: number }) {
  return (
    <div className="border-t border-(--uncf-line) pt-4.5 text-sm text-(--uncf-ink-2)">
      <b className="font-semibold text-(--uncf-ink)">What the numbers mean:</b> a final grade is one student finishing one
      course. The DFW rate is the share of final grades that were a D, F or W; incomplete, audit and missing grades aren’t
      counted. “Everyone else” is all the other students in the same course. A gap shows a difference between groups, not
      its cause.
      {hidesSmallGroups(minStudents) && ` Courses and groups with fewer than ${minStudents} students are hidden to protect privacy.`} One course code can appear
      under several names in the catalog. Some classes are listed twice in this data, so a few grades count twice.
      First-generation status isn’t shown because this data doesn’t record it consistently yet. The data is synthetic: it
      doesn’t describe real students.
    </div>
  );
}
