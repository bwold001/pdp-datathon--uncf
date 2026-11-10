import Link from "next/link";

import { Card, Counted, Legend, MessageCard, Notice, TrackBar, formatCount, formatShare, retentionWords } from "@/components/uncf/layout/explorer-parts";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

import type { BelowReasonKey, CountedStudents, CreditProgress, CreditsResponse, ProgressBandKey } from "./credits-data";

// The Credit momentum design without major: https://claude.ai/artifact/5pff2zd2e3VMP2ZPeZ5k9T ("Without major").

const fmt = (n: number) => n.toLocaleString("en-US");

/** Each year 1 group's name, its bar color and the text color on it, in the design's words and colors. */
const bandStyle: Record<ProgressBandKey, { name: (s: CreditProgress["settings"]) => string; fill: string; ink: string }> = {
  pace: { name: (s) => `On ${s.years}-year pace`, fill: "var(--uncf-blue)", ink: "#fff" },
  minimum: { name: (s) => `Did the minimum, slower than ${s.years} years`, fill: "var(--uncf-blue-mid)", ink: "var(--uncf-ink)" },
  below: { name: () => "Below the minimum", fill: "var(--uncf-orange)", ink: "var(--uncf-ink)" },
  stopped: { name: () => "Stopped after the first term", fill: "var(--uncf-grey-soft)", ink: "var(--uncf-ink)" },
};

/** The legend's short names for the same groups. */
const bandLegend: Record<ProgressBandKey, (s: CreditProgress["settings"]) => string> = {
  pace: (s) => `${s.years}-year pace`,
  minimum: () => "Minimum, slower",
  below: () => "Below minimum",
  stopped: () => "Stopped",
};

type CreditsViewProps = {
  data: CreditsResponse;
  /** The cohort bar's filters in words when any are set ("Pell recipient · Female"), and how to clear them. */
  filters?: { text: string; onClear: () => void };
  /** The cohort bar's query, so links to other tabs keep the same students. */
  linkQuery?: string;
};

/** The Credit momentum tab drawn from the API's progress answer: did students do the minimum, and are they on pace. */
export function CreditsView({ data, filters, linkQuery = "" }: CreditsViewProps) {
  const progress = data.progress;
  if (data.status === "suppressed" || !progress || !data.students) {
    return (
      <>
        <ProgressIntro data={data} />
        <MessageCard title="Fewer than 10 students match these filters.">
          Remove a filter to see results. Groups under 10 students are hidden to protect privacy.
        </MessageCard>
      </>
    );
  }
  const total = data.students;
  const words = retentionWords(data.meta.retention_type, data.meta.retention_term);
  const link = (href: string) => (linkQuery ? `${href}?${linkQuery}` : href);
  return (
    <>
      <ProgressIntro data={data} />
      {filters && (
        <div className="flex flex-wrap items-center gap-x-3.5 gap-y-2 rounded-lg bg-(--uncf-blue-tint) px-4 py-3">
          <span>
            Showing <b className="font-semibold">{fmt(total)} students</b>: {filters.text}. Every number below covers only these
            students.
          </span>
          <button
            type="button"
            onClick={filters.onClear}
            className="min-h-9 cursor-pointer rounded-lg border border-(--uncf-blue) bg-(--uncf-surface) px-3 font-semibold text-(--uncf-blue)"
          >
            Clear filters
          </button>
        </div>
      )}
      {data.meta.provisional && (
        <Notice title={`The ${data.meta.cohort} class’s second year is only partly in the data.`}>
          Year 2 numbers and {words.lower} for this class will change as the rest of that year arrives.
        </Notice>
      )}
      <div className="flex flex-wrap gap-5">
        <MinimumCard progress={progress} total={total} />
        <PaceCard progress={progress} total={total} />
      </div>
      <BandsCard progress={progress} retentionName={words.name} />
      <div className="flex flex-wrap gap-6">
        <BelowCard progress={progress} dfwHref={link(routes.uncfDfw)} />
        <YearTwoCard progress={progress} total={total} pathsHref={link(routes.uncfPaths)} />
      </div>
      <Counted>
        credits that count are earned credits in courses PDP marks college-level (CU) or developmental credit that applies
        (CC), in every term of year 1. Did the minimum = {progress.settings.minimum} or more in the year; fewer than{" "}
        {progress.settings.minimum} in a single year is below it, checked year by year. {progress.settings.years}-year pace =
        the school’s degree total ({progress.settings.degree_credits}) ÷ {progress.settings.years} years. This view doesn’t
        use major, so every student is measured against the same degree total. Students under {progress.settings.minimum}{" "}
        with no courses in their next fall or spring term count as stopped. Failed or withdrew goes by what cost the student
        more credits: F grades (the DFW tab’s rule: an F, or under 0.7) or withdrawals (W); a few students with incomplete or
        missing grades, or an even split, aren’t shown in a reason. Year 2 is every term of {progress.year_two}, judged on
        its own. {words.name}: {words.how}. Filters narrow every number on the page. Most students in this data seek an
        associate degree; {progress.settings.pace} a year is on-time pace for those too ({progress.settings.pace * 2}{" "}
        credits in 2 years).
      </Counted>
    </>
  );
}

/** The design's heading: which class, the question, and the rules every number uses. */
export function ProgressIntro({ data }: { data?: CreditsResponse }) {
  const settings = data?.progress?.settings;
  // The API names the first term when every student started in it (Fall 2022); otherwise it's the class's year.
  const first = data?.terms[0]?.label;
  const which = !data ? null : first && first !== "First term" ? `class that started ${first}` : `class that entered in ${data.meta.cohort}`;
  return (
    <div className="flex flex-col gap-3">
      <span className="text-sm font-semibold text-(--uncf-ink-3)">Credit momentum · year 1{which ? ` · ${which}` : ""}</span>
      <h2 className="text-[28px] font-semibold tracking-[-0.01em] text-balance md:text-[32px]">
        Are students making meaningful progress toward their degree?
      </h2>
      {settings && (
        <div className="flex flex-wrap gap-2 text-sm">
          <span className="rounded-full border border-(--uncf-line) bg-(--uncf-surface) px-3 py-1.5">
            <b className="font-semibold">Minimum:</b> {settings.minimum} credits a year ({settings.minimum / 2} a semester). Fewer
            than {settings.minimum} in any year is below it
          </span>
          <span className="rounded-full border border-(--uncf-line) bg-(--uncf-surface) px-3 py-1.5">
            <b className="font-semibold">{settings.years}-year pace:</b> {settings.degree_credits} credits ÷ {settings.years} years ={" "}
            {settings.pace} a year
          </span>
          <span className="rounded-full bg-(--uncf-chip) px-3 py-1.5 text-(--uncf-ink-2)">
            One degree total for every student · school setting
          </span>
        </div>
      )}
    </div>
  );
}

/** "About 1 in 5 did.": the share as one in so many students, or the words for none. */
function oneIn(share: number | null, verb: string, none: string): string {
  if (share === null) return "";
  if (share === 0) return none;
  return `${verb} About 1 in ${Math.max(1, Math.round(1 / share))}.`;
}

/** Credits a year as words: 30 or more a year, or more than 31 for a pace of 31.25. */
function aYear(credits: number): string {
  return Number.isInteger(credits) ? `${credits} or more a year` : `more than ${Math.floor(credits)} a year`;
}

/** Question 1: did they do the minimum in year 1, and again in year 2? */
function MinimumCard({ progress, total }: { progress: CreditProgress; total: number }) {
  const { minimum, settings } = progress;
  const yearTwo = progress.year_two_follow_up.status === "ok";
  return (
    <BigQuestion number={1} question="Did they do the minimum?" color="var(--uncf-blue-2)" share={minimum.share} answer={oneIn(minimum.share, "did.", "None did.")}>
      <p className="text-(--uncf-ink-2)">
        {formatCount(minimum.students)} of {fmt(total)} students earned {settings.minimum} or more credits that count toward a
        degree in their first year.
      </p>
      <BigQuestionNotes>
        {yearTwo ? (
          <span>
            <Strong>{formatShare(progress.both_years.share)}</Strong> did the minimum in year 1 and again in year 2 (
            {formatCount(progress.both_years.students)} students).
          </span>
        ) : (
          <span>Year 2 ({progress.year_two}) isn’t in the data yet, so it’s too soon to say who did it again.</span>
        )}
      </BigQuestionNotes>
    </BigQuestion>
  );
}

/** Question 2: are they on pace to finish in the degree's years? */
function PaceCard({ progress, total }: { progress: CreditProgress; total: number }) {
  const { pace, settings } = progress;
  const twoYears = progress.two_year_pace;
  return (
    <BigQuestion
      number={2}
      question={`Are they on pace to finish in ${settings.years} years?`}
      color="var(--uncf-blue)"
      share={pace.share}
      answer={oneIn(pace.share, "are.", "None are on pace.")}
      highlighted
    >
      <p className="text-(--uncf-ink-2)">
        {formatCount(pace.students)} of {fmt(total)} students earned {settings.pace} or more credits that count toward a degree
        in year 1.
      </p>
      <BigQuestionNotes>
        <span>
          <Strong>{formatShare(progress.higher_pace.share)}</Strong> if the school sets {settings.higher_degree_credits} credits (
          {aYear(settings.higher_pace)}).
        </span>
        {twoYears.status === "ok" ? (
          <span>
            <Strong>{formatShare(twoYears.share)}</Strong> are still on pace after 2 years ({settings.pace * 2} or more credits).
          </span>
        ) : (
          <span>Pace after 2 years: year 2 ({progress.year_two}) isn’t in the data yet.</span>
        )}
      </BigQuestionNotes>
    </BigQuestion>
  );
}

type BigQuestionProps = {
  number: number;
  question: string;
  color: string;
  share: number | null;
  answer: string;
  highlighted?: boolean;
  children: React.ReactNode;
};

/** One of the two questions: its big share, "About 1 in N", a sentence and notes under a rule. */
function BigQuestion({ number, question, color, share, answer, highlighted, children }: BigQuestionProps) {
  return (
    <section
      className={cn(
        "flex min-w-0 flex-[1_1_420px] flex-col gap-2.5 rounded-xl bg-(--uncf-surface) px-6 py-6 md:px-7.5 md:py-7",
        highlighted ? "border-2 border-(--uncf-blue)" : "border border-(--uncf-line)",
      )}
    >
      <h3 className={cn("text-[13px] font-semibold tracking-[0.04em] uppercase", highlighted ? "text-(--uncf-blue)" : "text-(--uncf-ink-3)")}>
        {number} · {question}
      </h3>
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="uncf-num text-[56px] leading-none font-medium tracking-[-0.03em] md:text-[72px]" style={{ color }}>
          {formatShare(share)}
        </span>
        <span className="text-xl leading-[1.3] font-semibold">{answer}</span>
      </div>
      {children}
    </section>
  );
}

/** The smaller lines under a question's answer. */
function BigQuestionNotes({ children }: { children: React.ReactNode }) {
  return <div className="mt-1.5 flex flex-col gap-1 border-t border-(--uncf-line) pt-3 text-sm text-(--uncf-ink-2)">{children}</div>;
}

/** A number in the notes, in the mono face. */
function Strong({ children }: { children: React.ReactNode }) {
  return <b className="uncf-num font-medium text-(--uncf-ink)">{children}</b>;
}

/** Where every student landed in year 1: one bar split by group, then each group with its count and retention. */
function BandsCard({ progress, retentionName }: { progress: CreditProgress; retentionName: string }) {
  const { settings } = progress;
  const ranges: Record<ProgressBandKey, string> = {
    pace: `${settings.pace} or more`,
    minimum: `${settings.minimum} to ${settings.pace - 1}`,
    below: `Under ${settings.minimum}`,
    stopped: `Under ${settings.minimum}, no courses in ${progress.next_term ?? "the next fall or spring term"}`,
  };
  const shownBands = progress.bands.filter((band) => band.share);
  return (
    <Card className="flex flex-col gap-5">
      <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
        <div>
          <h3 className="text-[22px] font-semibold">Where every student landed in year 1</h3>
          <p className="mt-1 text-(--uncf-ink-3)">Credits that count toward a degree, earned in the first year. Each student counted once.</p>
        </div>
        <Legend items={progress.bands.map((band) => ({ label: bandLegend[band.key](settings), color: bandStyle[band.key].fill }))} />
      </div>
      <div
        className="flex h-13 overflow-hidden rounded-lg font-semibold"
        role="img"
        aria-label={progress.bands.map((band) => `${bandStyle[band.key].name(settings)}: ${formatShare(band.share)}`).join(", ")}
      >
        {shownBands.map((band) => (
          <div
            key={band.key}
            className="uncf-num flex items-center overflow-hidden pl-2.5 whitespace-nowrap"
            style={{ flex: band.share!, background: bandStyle[band.key].fill, color: bandStyle[band.key].ink }}
          >
            {band.share! >= 0.06 ? formatShare(band.share) : ""}
          </div>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-160 border-collapse text-[15px]">
          <thead>
            <tr className="border-b border-(--uncf-line-2) text-left text-[13px] font-medium text-(--uncf-ink-3)">
              <th className="py-2 pr-3 font-medium">Group</th>
              <th className="py-2 pr-3 font-medium">Credits that count, year 1</th>
              <th className="py-2 pr-3 text-right font-medium">Students</th>
              <th className="py-2 text-right font-medium">{retentionName}</th>
            </tr>
          </thead>
          <tbody>
            {progress.bands.map((band) => (
              <tr key={band.key} className="border-b border-(--uncf-line)">
                <td className="py-3 pr-3 font-semibold">
                  <span className="inline-flex items-center gap-2">
                    <span className="size-3 flex-none rounded-[3px]" style={{ background: bandStyle[band.key].fill }} aria-hidden />
                    {bandStyle[band.key].name(settings)}
                  </span>
                </td>
                <td className="py-3 pr-3">{ranges[band.key]}</td>
                <td className="uncf-num py-3 pr-3 text-right">{countAndShare(band)}</td>
                <td className="uncf-num py-3 text-right">{formatShare(band.retention.rate)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {progress.unsorted !== 0 && (
        <p className="text-[13px] text-(--uncf-ink-3)">
          {formatCount(progress.unsorted)} students under the minimum aren’t in a group: their next fall or spring term isn’t in
          the data yet, or their starting term is unknown.
        </p>
      )}
    </Card>
  );
}

/** "778 · 51%", or "Under 10" alone when the group is hidden. */
function countAndShare(counted: CountedStudents): string {
  return counted.students === null ? "Under 10" : `${fmt(counted.students)} · ${formatShare(counted.share)}`;
}

/** Each reason's words and what to act on, in the design's words. */
const reasonText: Record<BelowReasonKey, { label: (minimum: number) => string; note: string; dfwLink?: boolean }> = {
  under: { label: (minimum) => `Signed up for fewer than ${minimum}`, note: "Never had a full load. Act on: registration and advising." },
  failed: { label: () => "Signed up for enough, failed", note: "Lost more credits to F grades than to withdrawals.", dfwLink: true },
  withdrew: { label: () => "Signed up for enough, withdrew", note: "Lost more credits to withdrawals (W) than to F grades.", dfwLink: true },
  not_counted: { label: () => "Passed enough, not all of it counts", note: "Developmental or other credit that doesn’t apply to a degree." },
};

/** Why the students still taking courses fell below the minimum. Hidden when they're under 10. */
function BelowCard({ progress, dfwHref }: { progress: CreditProgress; dfwHref: string }) {
  const { below, settings } = progress;
  return (
    <SideCard
      title={below.students === null ? "Why students fell below the minimum" : `Why ${fmt(below.students)} fell below the minimum`}
      subtitle={`Students still taking courses in ${progress.next_term ?? "their next fall or spring term"} who ended year 1 under ${settings.minimum} credits that count`}
    >
      {below.students === null ? (
        <p className="text-(--uncf-ink-2)">Fewer than 10 of these students fell below the minimum, so the reasons are hidden.</p>
      ) : below.students === 0 ? (
        <p className="text-(--uncf-ink-2)">None of these students fell below the minimum.</p>
      ) : (
        <>
          {below.reasons.map((reason) => (
            <ShareRow key={reason.key} label={reasonText[reason.key].label(settings.minimum)} counted={reason} color="var(--uncf-orange)">
              {reasonText[reason.key].note}
              {reasonText[reason.key].dfwLink && (
                <>
                  {" "}
                  <Link href={dfwHref} className="text-(--uncf-blue) underline">
                    Which courses: DFW tab
                  </Link>
                </>
              )}
            </ShareRow>
          ))}
          {below.unexplained !== 0 && (
            <p className="text-[13px] text-(--uncf-ink-3)">
              {formatCount(below.unexplained)} more had incomplete or missing grades, or lost as many credits to F grades as to
              withdrawals, so they aren’t in a reason.
            </p>
          )}
        </>
      )}
    </SideCard>
  );
}

/** What the students who did the minimum in year 1 did in year 2. */
function YearTwoCard({ progress, total, pathsHref }: { progress: CreditProgress; total: number; pathsHref: string }) {
  const { year_two_follow_up: followUp, settings } = progress;
  return (
    <SideCard
      title="Did they keep it up in year 2?"
      subtitle={`The ${formatCount(followUp.students)} students who did the minimum in year 1, and what they did in year 2 (${progress.year_two})`}
    >
      {followUp.students === null ? (
        <p className="text-(--uncf-ink-2)">Fewer than 10 of these students did the minimum in year 1, so year 2 is hidden.</p>
      ) : followUp.status !== "ok" ? (
        <p className="text-(--uncf-ink-2)">Year 2 ({progress.year_two}) isn’t in the data yet for this class.</p>
      ) : (
        <>
          <ShareRow label="Did the minimum again" counted={followUp.again} color="var(--uncf-blue)">
            {settings.minimum} or more credits that count, two years running.
          </ShareRow>
          <ShareRow label={`Kept taking courses, fell under ${settings.minimum}`} counted={followUp.kept_taking_courses} color="var(--uncf-orange)">
            Still enrolled, but below the minimum in year 2. Act on: advising before year-2 registration.
          </ShareRow>
          <ShareRow label="Took no courses in year 2" counted={followUp.no_courses} color="var(--uncf-grey)">
            Did the minimum, then left.{" "}
            <Link href={pathsHref} className="text-(--uncf-blue) underline">
              Where they went: Student paths
            </Link>
          </ShareRow>
          <p className="rounded-lg bg-(--uncf-blue-tint) px-3.5 py-3 text-sm">
            Only {formatCount(progress.both_years.students)} of {fmt(total)} students ({formatShare(progress.both_years.share)}) did
            the minimum in both years.
          </p>
        </>
      )}
    </SideCard>
  );
}

/** One of the two cards side by side under the groups. */
function SideCard({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <Card className="flex flex-[1_1_440px] flex-col gap-4">
      <div>
        <h3 className="text-[21px] font-semibold">{title}</h3>
        <p className="mt-1 text-(--uncf-ink-3)">{subtitle}</p>
      </div>
      {children}
    </Card>
  );
}

/** A labelled count and share with its bar, and a note under it. */
function ShareRow({ label, counted, color, children }: { label: string; counted: CountedStudents; color: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between gap-3">
        <span className="font-medium">{label}</span>
        <span className="uncf-num">{countAndShare(counted)}</span>
      </div>
      <TrackBar share={counted.share} color={color} height={22} label={`${label}: ${countAndShare(counted)}`} />
      <span className="text-sm text-(--uncf-ink-3)">{children}</span>
    </div>
  );
}
