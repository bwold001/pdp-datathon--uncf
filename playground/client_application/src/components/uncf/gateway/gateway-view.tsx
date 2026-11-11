"use client";

import { useState } from "react";

import { Card, CardHead, MessageCard, Notice, formatShare, retentionWords } from "@/components/uncf/layout/explorer-parts";
import { explorerButton } from "@/components/uncf/layout/explorer-styles";
import { hidesSmallGroups, privacyNote, tooFew } from "@/components/uncf/layout/small-groups";
import { cn } from "@/lib/utils";

import {
  type CoursePair,
  type GatewayCourse,
  type GatewayResponse,
  type GatewaySort,
  gatewaySorts,
  pathSteps,
  sortCourses,
  subjectLabel,
} from "./gateway-data";

const fmt = (n: number) => n.toLocaleString("en-US");
const PAGE = 10;
const rowGrid =
  "grid grid-cols-[minmax(0,1fr)_72px] items-center gap-3 sm:grid-cols-[minmax(0,1.3fr)_64px_62px_66px_76px_70px_62px]";

type GatewayViewProps = {
  data: GatewayResponse;
  /** The filters as a group name, e.g. "Pell (year 1): Pell recipient"; null when none is set. */
  groupLabel?: string | null;
};

/** The Gateway courses tab: the course list, the selected course's path and group gap, and the course pairs. */
export function GatewayView({ data, groupLabel = null }: GatewayViewProps) {
  const [sort, setSort] = useState<GatewaySort>("size");
  const [shown, setShown] = useState(PAGE);
  const [chosen, setChosen] = useState<string | null>(null);

  if (data.status === "suppressed" || !data.students || !data.cohort_retention) {
    return (
      <MessageCard title={`${tooFew(data.meta.min_students)} match these filters.`}>
        Remove a filter to see results. {privacyNote(data.meta.min_students)}
      </MessageCard>
    );
  }
  const activeSort = sort === "gap" && !data.meta.compared ? "size" : sort;
  const courses = sortCourses(data.courses, activeSort);
  const selected = courses.find((course) => course.course === chosen) ?? courses[0] ?? null;

  return (
    <>
      {!data.meta.flagged && (
        <Notice title="No gateway courses are flagged in this PDP submission.">
          The institution hasn’t marked any {data.meta.year_one} grades as gateway math or English, so no course is listed.
        </Notice>
      )}
      {data.meta.provisional && (
        <Notice title="The next year is only partly in the data.">
          Retention for the {data.meta.cohort} class will change as the rest of that year arrives.
        </Notice>
      )}
      <div className="grid items-start gap-5 min-[961px]:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
        <CourseList
          data={data}
          courses={courses.slice(0, shown)}
          total={courses.length}
          sort={activeSort}
          groupLabel={groupLabel}
          selected={selected?.course ?? null}
          onSelect={setChosen}
          onSort={(next) => {
            setSort(next);
            setShown(PAGE);
          }}
          onMore={courses.length > shown ? () => setShown(shown + PAGE) : undefined}
        />
        {selected && <CourseDetail course={selected} compared={data.meta.compared} groupLabel={groupLabel} minStudents={data.meta.min_students} />}
      </div>
      <PairsCard data={data} />
      <GatewayCounted data={data} />
    </>
  );
}

type CourseListProps = {
  data: GatewayResponse;
  courses: GatewayCourse[];
  total: number;
  sort: GatewaySort;
  groupLabel: string | null;
  selected: string | null;
  onSelect: (course: string) => void;
  onSort: (sort: GatewaySort) => void;
  onMore?: () => void;
};

/** The gateway courses, one row each, with what every column means. */
function CourseList({ data, courses, total, sort, groupLabel, selected, onSelect, onSort, onMore }: CourseListProps) {
  return (
    <Card>
      <CardHead
        className="mb-2.5"
        title="Gateway courses"
        subtitle={`${fmt(total)} courses have ${data.meta.year_one} grades the school marked as a gateway course`}
        aside={
          <label className="inline-flex items-center gap-2 text-sm text-(--uncf-ink-2)">
            Sort by
            <select
              value={sort}
              onChange={(event) => onSort(event.target.value as GatewaySort)}
              className="rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-2.5 py-1.75"
            >
              {(Object.keys(gatewaySorts) as GatewaySort[]).map((option) => (
                <option key={option} value={option} disabled={option === "gap" && !data.meta.compared}>
                  {gatewaySorts[option]}
                </option>
              ))}
            </select>
          </label>
        }
      />
      <p className="mb-1.5 text-[13px] text-(--uncf-ink-3)">
        <b className="font-semibold text-(--uncf-ink-2)">First try / In the end:</b> share who passed on the first try / on
        any try in year 1. <b className="font-semibold text-(--uncf-ink-2)">Retention if passed / if not passed:</b> share{" "}
        {retentionWords(data.meta.retention_type, data.meta.retention_term).lower}, among students who passed vs. never
        passed.{" "}
        <b className="font-semibold text-(--uncf-ink-2)">Group gap:</b> your filtered group’s first-try pass rate minus
        everyone else’s.
      </p>
      <p className="mb-3.5 text-[13px] text-(--uncf-ink-3)">
        {groupLabel
          ? `Comparing ${groupLabel} with everyone else who took each course.`
          : "Pick a group in the filters above to compare it with everyone else in each course."}
      </p>
      <div className={cn(rowGrid, "hidden border-b border-(--uncf-line-2) px-2.5 pb-2 text-[13px] leading-tight font-semibold text-(--uncf-ink-3) sm:grid")}>
        <span>Course</span>
        <span className="text-right">Students</span>
        <span className="text-right">First try</span>
        <span className="text-right">In the end</span>
        <span className="text-right">Retention if passed</span>
        <span className="text-right">if not passed</span>
        <span className="text-right">Group gap</span>
      </div>
      {courses.length === 0 ? (
        <p className="px-2.5 py-4 text-[13px] text-(--uncf-ink-3)">No gateway course has {data.meta.min_students} or more students with these filters.</p>
      ) : (
        <ul>
          {courses.map((course) => (
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
                  <span className="uncf-num text-sm font-semibold">{course.course}</span>
                  <span className="block truncate text-[13px] text-(--uncf-ink-3)">
                    {subjectLabel[course.subject]}
                    {course.name ? ` · ${course.name}` : ""}
                  </span>
                </span>
                <span className="uncf-num hidden text-right sm:block">{fmt(course.students)}</span>
                <span className="uncf-num text-right font-medium">{formatShare(course.first_pass / course.students)}</span>
                <span className="uncf-num hidden text-right sm:block">{formatShare(course.passed / course.students)}</span>
                <RetentionCell rate={course.retained_if_passed.rate} />
                <RetentionCell rate={course.retained_if_not_passed.rate} />
                <GapCell course={course} />
              </button>
            </li>
          ))}
        </ul>
      )}
      {onMore && (
        <button type="button" className={cn(explorerButton, "mt-3.5")} onClick={onMore}>
          Show {PAGE} more of {fmt(total)}
        </button>
      )}
    </Card>
  );
}

/** A retention share in the list, or "hidden" for a group under min_students. */
function RetentionCell({ rate }: { rate: number | null }) {
  return rate === null ? (
    <span className="hidden text-right text-xs text-(--uncf-ink-3) sm:block">hidden</span>
  ) : (
    <span className="uncf-num hidden text-right sm:block">{formatShare(rate)}</span>
  );
}

/** The group gap in the list: "–" with no filter, "hidden" when too small, else signed points. */
function GapCell({ course }: { course: GatewayCourse }) {
  const group = course.group;
  if (!group) return <span className="hidden text-right text-(--uncf-ink-3) sm:block">–</span>;
  if (group.status !== "ok") return <span className="hidden text-right text-xs text-(--uncf-ink-3) sm:block">hidden</span>;
  return (
    <span className={cn("uncf-num hidden text-right sm:block", group.gap! < 0 ? "text-(--uncf-orange-ink)" : "text-(--uncf-blue)")}>
      {signedPoints(group.gap!)}
    </span>
  );
}

/** Points with a real minus sign, e.g. −6.2 or +3.0. */
function signedPoints(gap: number): string {
  return `${gap < 0 ? "−" : "+"}${Math.abs(gap).toFixed(1)}`;
}

type CourseDetailProps = { course: GatewayCourse; compared: boolean; groupLabel: string | null; minStudents: number };

/** The selected course: first try and in the end, what happened after the first try, and your group. */
function CourseDetail({ course, compared, groupLabel, minStudents }: CourseDetailProps) {
  return (
    <section aria-live="polite" className="min-[961px]:sticky min-[961px]:top-4">
      <Card className="flex flex-col gap-4.5">
        <div>
          <div className="mb-1.5 text-xs font-bold tracking-widest text-(--uncf-ink-2) uppercase">
            Selected gateway course · {subjectLabel[course.subject]}
          </div>
          <h3 className="uncf-num text-[21px] font-semibold">{course.course}</h3>
          {course.name && <p className="mt-1 text-(--uncf-ink-3)">Listed in the catalog as {course.name}</p>}
        </div>
        <div className="flex flex-wrap gap-x-12 gap-y-4">
          <BigShare share={course.first_pass / course.students} note={`passed on the first try: ${fmt(course.first_pass)} of ${fmt(course.students)} students`} />
          <BigShare share={course.passed / course.students} note="passed in the end" />
        </div>
        <Section title="What happened after the first try">
          <p className="text-[13px] text-(--uncf-ink-3)">
            Every student who took {course.course} in year 1, by how it went. “Didn’t retake” are students who could still
            be reached.
          </p>
          <PathBar course={course} />
        </Section>
        <Section title="Your group vs. everyone else">
          <p className="text-[13px] text-(--uncf-ink-3)">
            First-try pass rate for the group picked in the filters, next to all other students in {course.course}.
          </p>
          <GroupCompare course={course} compared={compared} groupLabel={groupLabel} minStudents={minStudents} />
        </Section>
      </Card>
    </section>
  );
}

/** A large share with a short note under it. */
function BigShare({ share, note }: { share: number; note: string }) {
  return (
    <div>
      <div className="uncf-num text-[38px] leading-[1.1] font-medium">{formatShare(share)}</div>
      <div className="text-[13px] text-(--uncf-ink-3)">{note}</div>
    </div>
  );
}

/** A titled block in the detail card. */
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3 border-t border-(--uncf-line) pt-4">
      <h3 className="text-[17px] font-semibold">{title}</h3>
      {children}
    </div>
  );
}

/** The four steps after the first try as one bar, with a legend that names hidden steps. */
function PathBar({ course }: { course: GatewayCourse }) {
  const label = pathSteps.map((step) => `${step.label}: ${course.path[step.key] ?? "hidden"}`).join(", ");
  return (
    <>
      <div className="flex h-7.5 overflow-hidden rounded-[4px] bg-(--uncf-track)" role="img" aria-label={label}>
        {pathSteps.map((step) => {
          const count = course.path[step.key];
          return count ? <div key={step.key} style={{ flex: count, background: step.color }} title={`${step.label}: ${fmt(count)}`} /> : null;
        })}
      </div>
      <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {pathSteps.map((step) => {
          const count = course.path[step.key];
          return (
            <div key={step.key} className="flex items-center gap-2 text-sm">
              <i className="size-3 flex-none rounded-[3px]" style={{ background: step.color }} aria-hidden />
              <span className="flex-1">{step.label}</span>
              <span className="uncf-num">{count === null ? "hidden" : fmt(count)}</span>
            </div>
          );
        })}
      </div>
    </>
  );
}

/** The filtered group's first-try pass rate next to everyone else's, or why it can't be shown. */
function GroupCompare({ course, compared, groupLabel, minStudents }: CourseDetailProps) {
  const group = course.group;
  if (!compared || !group) {
    return <p className="text-[13px] text-(--uncf-ink-3)">Pick a group in the filters above, such as Pell or Full / part-time.</p>;
  }
  if (group.status !== "ok") {
    return (
      <p className="text-[13px] text-(--uncf-ink-3)">
        Hidden in this course: {hidesSmallGroups(minStudents) ? `under ${minStudents} students in the group, or too few others.` : "no students to compare with."}
      </p>
    );
  }
  const bars = [
    { label: groupLabel ?? "Your group", rate: group.rate!, color: "var(--uncf-blue)" },
    { label: "Everyone else", rate: group.others_rate!, color: "var(--uncf-grey)" },
  ];
  const behind = group.gap! < 0;
  return (
    <>
      <div className="flex flex-col gap-3">
        {bars.map((bar) => (
          <div key={bar.label}>
            <div className="flex justify-between gap-3 text-sm">
              <span className="min-w-0">{bar.label}</span>
              <span className="uncf-num">{formatShare(bar.rate)}</span>
            </div>
            <div className="mt-1 h-3 rounded-[3px] bg-(--uncf-track)">
              <div className="h-full rounded-[3px]" style={{ width: `${bar.rate * 100}%`, background: bar.color }} />
            </div>
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-1 border-t border-(--uncf-line) pt-3.5 text-sm text-(--uncf-ink-2)">
        <span className={cn("uncf-num text-[26px]", behind ? "text-(--uncf-orange-ink)" : "text-(--uncf-blue)")}>{signedPoints(group.gap!)} pts</span>
        <span>
          This group passes on the first try {behind ? "less" : "more"} often than everyone else.{" "}
          {group.likely_noise ? "Could be chance." : "Unlikely to be chance."}
        </span>
      </div>
    </>
  );
}

/** Gateway courses taken with another course in the first term, where fewer students came back than everyone else. */
function PairsCard({ data }: { data: GatewayResponse }) {
  const when = data.meta.first_term ? `in ${data.meta.first_term}` : "in their first term";
  const words = retentionWords(data.meta.retention_type, data.meta.retention_term);
  return (
    <Card>
      <CardHead
        title="Course pairs with lower retention"
        subtitle={
          <span className="block max-w-[70ch]">
            A gateway course and another course taken together in a student’s first term, where fewer students were{" "}
            {words.lower} than everyone else. Biggest effect first. This shows a pattern worth looking into, not the cause.
          </span>
        }
        aside={
          <div className="self-end text-(--uncf-ink-2)">
            {words.name}, these students: <b className="uncf-num">{formatShare(data.cohort_retention!.rate)}</b>
          </div>
        }
      />
      {data.pairs.length === 0 ? (
        <p className="text-(--uncf-ink-3)">No course pair has lower retention than everyone else.</p>
      ) : (
        <div className="grid gap-4 min-[961px]:grid-cols-3">
          {data.pairs.map((pair) => (
            <PairCard key={pair.courses.join("+")} pair={pair} when={when} outcome={words.lower} />
          ))}
        </div>
      )}
      <p className="mt-4 text-[13px] text-(--uncf-ink-3)">
        {fmt(data.pairs_considered)} pairs have {data.meta.min_pair_students} or more students and are compared; the rest
        are hidden to protect privacy. “Could be chance” means the gap may not hold up in another year.
      </p>
    </Card>
  );
}

/** One course pair: its retention, the gap to everyone else, and how many took both. */
function PairCard({ pair, when, outcome }: { pair: CoursePair; when: string; outcome: string }) {
  const chip = "uncf-num inline-block rounded-[5px] bg-(--uncf-chip) px-2.5 py-0.75 font-semibold";
  return (
    <div className="rounded-[10px] border border-(--uncf-line) px-5.5 py-5">
      <span className={chip}>{pair.courses[0]}</span>
      {" + "}
      <span className={chip}>{pair.courses[1]}</span>
      <div className="mt-3.5 mb-1.5">
        <span className="uncf-num text-[34px] font-medium">{formatShare(pair.rate)}</span>
        <span className="ml-2 font-semibold text-(--uncf-orange-ink)">{signedPoints(pair.gap)} pts vs. everyone else</span>
      </div>
      <div className="text-(--uncf-ink-3)">
        {fmt(pair.retained)} of {fmt(pair.students)} students who took both {when}: {outcome}
        {pair.likely_noise ? " · could be chance" : ""}
      </div>
    </div>
  );
}

/** The note under the page: what the numbers mean, in the design's words. */
function GatewayCounted({ data }: { data: GatewayResponse }) {
  return (
    <div className="border-t border-(--uncf-line) pt-4.5 text-sm text-(--uncf-ink-2)">
      <b className="font-semibold text-(--uncf-ink)">What the numbers mean:</b> every number counts students, once per course,
      in their first year ({data.meta.year_one}), the same window as the PDP’s gateway measure. Only grades the school marked
      as gateway math or English count. Passed: a grade of 1.0 or higher, or a Pass; the DFW page uses 2.0. A try is a
      term, and the first try is the earliest. Retention follows the Retention filter above: “
      {retentionWords(data.meta.retention_type, data.meta.retention_term).name}” means{" "}
      {retentionWords(data.meta.retention_type, data.meta.retention_term).how}. Everyone else is all other students who took the same course. A gap shows a difference, not its cause.
      {hidesSmallGroups(data.meta.min_students) &&
        ` Courses and groups with fewer than ${data.meta.min_students} students are hidden to protect privacy${data.hidden_courses ? ` (${fmt(data.hidden_courses)} courses)` : ""}.`}{" "}
      The data is synthetic: it doesn’t describe real students.
    </div>
  );
}
