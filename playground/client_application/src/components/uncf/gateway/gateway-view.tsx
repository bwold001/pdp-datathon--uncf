"use client";

import { useState } from "react";

import { Card, CardHead, Counted, Legend, MessageCard, Notice, formatShare, tableClasses } from "@/components/uncf/layout/explorer-parts";
import { explorerButton } from "@/components/uncf/layout/explorer-styles";
import { hidesSmallGroups, privacyNote, tooFew } from "@/components/uncf/layout/small-groups";
import { cn } from "@/lib/utils";

import { type GatewayCourse, type GatewayResponse, outcomeStyle, subjectLabel } from "./gateway-data";

const fmt = (n: number) => n.toLocaleString("en-US");
// Before "Show all": the biggest few courses in each subject, so math and English both show.
const FIRST_PER_SUBJECT = 5;

/** The Gateway courses tab drawn from the API's answer: notices, the outcomes table and the high-risk pairs. */
export function GatewayView({ data }: { data: GatewayResponse }) {
  if (data.status === "suppressed" || !data.students || !data.cohort_retention) {
    return (
      <MessageCard title={`${tooFew(data.meta.min_students)} match these filters.`}>
        Remove a filter to see results. {privacyNote(data.meta.min_students)}
      </MessageCard>
    );
  }
  return (
    <>
      {!data.meta.flagged && (
        <Notice title="Gateway courses not yet flagged in this PDP submission.">
          Showing inferred first-year math and English courses until the institution flags them in its next submission.
        </Notice>
      )}
      {data.meta.provisional && (
        <Notice title={`${data.meta.retention_term} is only partly in the data.`}>
          Next-fall retention for the {data.meta.cohort} class will rise as the rest of that term arrives.
        </Notice>
      )}
      <OutcomesCard data={data} />
      <PairsCard data={data} />
    </>
  );
}

/** The gateway outcomes table: students, the outcome bar, and next-fall retention for passed and not passed. */
function OutcomesCard({ data }: { data: GatewayResponse }) {
  const [showAll, setShowAll] = useState(false);
  const first = (["E", "M"] as const).flatMap((subject) => data.courses.filter((c) => c.subject === subject).slice(0, FIRST_PER_SUBJECT));
  const courses = showAll ? data.courses : first;
  const leftOut = data.courses.reduce((total, course) => total + (course.other ?? 0), 0);

  return (
    <Card>
      <CardHead
        title="Gateway course outcomes"
        subtitle={`First attempts in year 1 by students who entered in ${data.meta.cohort}`}
        aside={<Legend items={outcomeStyle.map((outcome) => ({ label: outcome.label, color: outcome.color }))} />}
      />
      {data.courses.length === 0 ? (
        <p className="text-(--uncf-ink-3)">No gateway course has {data.meta.min_students} or more students with these filters.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className={tableClasses.table}>
            <thead>
              <tr>
                <th className={tableClasses.th}>Course</th>
                <th className={cn(tableClasses.th, tableClasses.right, "pr-8")}>Students</th>
                <th className={tableClasses.th}>Outcome</th>
                <th className={cn(tableClasses.th, tableClasses.right, "pl-4")}>Next-fall retention if passed</th>
                <th className={cn(tableClasses.th, tableClasses.right, "pl-4")}>if not passed</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((course) => (
                <tr key={course.course}>
                  <td className={cn(tableClasses.td, "align-middle")}>
                    <div className="font-semibold">{course.course}</div>
                    <div className="text-sm text-(--uncf-ink-3)">
                      {course.name ? `${course.name} · ` : ""}
                      {subjectLabel[course.subject]}
                    </div>
                  </td>
                  <td className={cn(tableClasses.td, tableClasses.right, "uncf-num pr-8 align-middle")}>{fmt(course.students)}</td>
                  <td className={cn(tableClasses.td, "w-[42%] min-w-55 align-middle")}>
                    <OutcomeBar course={course} />
                  </td>
                  <td className={cn(tableClasses.td, tableClasses.right, "uncf-num pl-4 align-middle text-(--uncf-blue)")}>
                    {formatShare(course.retained_if_passed.rate)}
                  </td>
                  <td className={cn(tableClasses.td, tableClasses.right, "uncf-num pl-4 align-middle text-(--uncf-orange-ink)")}>
                    {formatShare(course.retained_if_not_passed.rate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {data.courses.length > first.length && (
        <button type="button" className={cn(explorerButton, "mt-4")} onClick={() => setShowAll(!showAll)}>
          {showAll ? `Show the ${FIRST_PER_SUBJECT} biggest in each subject` : `Show all ${data.courses.length} courses`}
        </button>
      )}
      <Counted>
        each student’s first attempt at each gateway course in year 1. Passed: a grade of 2.0 (a C) or better, or a pass. D
        or F: under 2.0, or an F. Withdrew: a W. Each bar is the share of students with one of those grades
        {leftOut > 0 ? `; ${fmt(leftOut)} with an incomplete, audit or missing grade are left out` : ""}. Next-fall
        retention: took a course here in {data.meta.retention_term}. Gateway courses are the ones{" "}
        {data.meta.flagged
          ? "the institution flags as gateway math or English in the PDP course file"
          : "inferred from year-1 college-level courses with a math or English prefix"}
        .
        {hidesSmallGroups(data.meta.min_students) &&
          ` Courses with fewer than ${data.meta.min_students} students${data.hidden_courses ? ` (${fmt(data.hidden_courses)})` : ""} are hidden; “–” is a group under ${data.meta.min_students} students.`}
      </Counted>
    </Card>
  );
}

/** One course's outcomes as a bar that totals 100%, with the share in each part when there's room. */
function OutcomeBar({ course }: { course: GatewayCourse }) {
  const parts = outcomeStyle.map((outcome) => ({ ...outcome, share: course[outcome.key] / course.students }));
  const label = parts.map((part) => `${Math.round(part.share * 100)}% ${part.label.toLowerCase()}`).join(", ");
  return (
    <div className="uncf-num flex h-6.5 overflow-hidden rounded-[3px] text-[13px]" role="img" aria-label={label}>
      {parts.map((part) =>
        part.share > 0 ? (
          <div
            key={part.key}
            className="flex items-center overflow-hidden pl-2 whitespace-nowrap"
            style={{ flex: part.share, background: part.color, color: part.text }}
          >
            {part.share >= 0.08 ? `${Math.round(part.share * 100)}%` : ""}
          </div>
        ) : null,
      )}
    </div>
  );
}

/** Course pairs from the first term whose next-fall retention is below the cohort's. */
function PairsCard({ data }: { data: GatewayResponse }) {
  const when = data.meta.first_term ? `in ${data.meta.first_term}` : "in their first term";
  return (
    <Card>
      <CardHead
        title="High-risk course pairs"
        subtitle={
          <span className="block max-w-[70ch]">
            Courses taken in the same first term where next-fall retention falls below the cohort’s. This shows a pattern
            worth looking into, not the cause.
          </span>
        }
        aside={
          <div className="self-end text-(--uncf-ink-2)">
            Cohort retention: <b className="uncf-num">{formatShare(data.cohort_retention!.rate)}</b>
          </div>
        }
      />
      {data.pairs.length === 0 ? (
        <p className="text-(--uncf-ink-3)">
          No pair of first-term courses taken by {data.meta.min_pair_students} or more students has next-fall retention
          below the cohort’s.
        </p>
      ) : (
        <div className="grid gap-4 min-[961px]:grid-cols-3">
          {data.pairs.map((pair) => (
            <div key={pair.courses.join("+")} className="rounded-[10px] border border-(--uncf-line) px-5.5 py-5">
              <span className="uncf-num inline-block rounded-[5px] bg-(--uncf-chip) px-2.5 py-0.75 font-semibold">{pair.courses[0]}</span>
              {" + "}
              <span className="uncf-num inline-block rounded-[5px] bg-(--uncf-chip) px-2.5 py-0.75 font-semibold">{pair.courses[1]}</span>
              <div className="mt-3.5 mb-1.5">
                <span className="uncf-num text-[34px] font-medium">{formatShare(pair.rate)}</span>
                <span className="ml-2 font-semibold text-(--uncf-orange-ink)">−{Math.abs(Math.round(pair.gap))} pts vs. cohort</span>
              </div>
              <div className="text-(--uncf-ink-3)">
                {fmt(pair.students)} students took both {when}
              </div>
            </div>
          ))}
        </div>
      )}
      <p className="mt-4 text-[13px] text-(--uncf-ink-3)">
        Pairs taken together by {data.meta.min_pair_students} or more students: {fmt(data.pairs_considered)}. Showing the{" "}
        {data.pairs.length === 1 ? "one" : data.pairs.length} furthest below the cohort’s next-fall retention (
        {data.meta.retention_term}).
      </p>
    </Card>
  );
}
