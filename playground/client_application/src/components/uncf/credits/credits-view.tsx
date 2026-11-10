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
  retentionWords,
  tableClasses,
} from "@/components/uncf/layout/explorer-parts";
import { cn } from "@/lib/utils";

import { type CreditsResponse, milestoneLabel, tierStyle } from "./credits-data";

const fmt = (n: number) => n.toLocaleString("en-US");
const one = (n: number | null) => (n === null ? "–" : n.toFixed(1));

/** The Credit momentum tab drawn from the API's answer: tiles, milestones, the first two terms and the tiers. */
export function CreditsView({ data }: { data: CreditsResponse }) {
  if (data.status === "suppressed" || !data.credits || !data.completion) {
    return (
      <MessageCard title="Fewer than 10 students with year-1 credits match these filters.">
        Remove a filter to see results. Groups under 10 students are hidden to protect privacy.
      </MessageCard>
    );
  }
  return (
    <>
      {data.meta.provisional && (
        <Notice title={`The ${data.meta.cohort} class’s second year is only partly in the data.`}>
          {retentionWords(data.meta.retention_type, data.meta.retention_term).name} for this class will rise as the rest of
          that year arrives.
        </Notice>
      )}
      <KpiGrid columns={3}>
        <Kpi label="Avg. credits attempted · year 1" value={one(data.credits.avg_attempted)} note="Per student, every term of year 1" />
        <Kpi label="Avg. credits earned · year 1" value={one(data.credits.avg_earned)} tone="blue" note="Per student, every term of year 1" />
        <Kpi
          label="Credit completion ratio"
          value={formatShare(data.completion.ratio)}
          note="PDP name: Credit Completion Ratio · each student’s earned ÷ attempted, averaged"
        />
      </KpiGrid>
      <TwoColumns>
        <MilestonesCard data={data} />
        <TermsCard data={data} />
      </TwoColumns>
      <TiersCard data={data} />
    </>
  );
}

/** How many students reached 12, 24 and 30 credits in year 1. */
function MilestonesCard({ data }: { data: CreditsResponse }) {
  return (
    <Card>
      <CardHead title="Progress toward credit milestones" subtitle="Share of the cohort that earned at least this many credits in year 1" />
      <div className="flex flex-col gap-5.5">
        {data.milestones.map((milestone) => (
          <div key={milestone.credits} className="flex flex-col gap-1.5">
            <div className="flex justify-between gap-3">
              <span>{milestoneLabel[milestone.credits]}</span>
              <span className="uncf-num">
                {formatCount(milestone.students)}
                {milestone.share !== null && ` · ${formatShare(milestone.share)}`}
              </span>
            </div>
            <TrackBar
              share={milestone.share}
              color="var(--uncf-blue)"
              height={24}
              label={`${milestoneLabel[milestone.credits]}: ${formatCount(milestone.students)} students`}
            />
          </div>
        ))}
      </div>
    </Card>
  );
}

/** Average credits attempted and earned in the first two terms, as side-by-side columns. */
function TermsCard({ data }: { data: CreditsResponse }) {
  const values = data.terms.flatMap((term) => [term.avg_attempted ?? 0, term.avg_earned ?? 0]);
  // The tallest column reaches about 85% of the chart, as in the design, so its label fits above it.
  const top = Math.max(...values, 1) * 1.15;
  const label = data.terms
    .map((term) => `${term.label}: ${term.avg_attempted === null ? "hidden" : `${one(term.avg_attempted)} attempted, ${one(term.avg_earned)} earned`}`)
    .join(". ");

  return (
    <Card>
      <CardHead
        className="mb-2"
        title="Attempted vs. earned, by term"
        subtitle="Average credits per student enrolled that term"
        aside={
          <Legend
            items={[
              { label: "Attempted", color: "var(--uncf-blue-soft)" },
              { label: "Earned", color: "var(--uncf-blue)" },
            ]}
          />
        }
      />
      <div className="flex h-65 items-end justify-around border-b border-(--uncf-line-2) px-2" role="img" aria-label={label}>
        {data.terms.map((term) => (
          <div key={term.label} className="flex h-full items-end gap-3.5">
            {[
              { value: term.avg_attempted, color: "var(--uncf-blue-soft)" },
              { value: term.avg_earned, color: "var(--uncf-blue)" },
            ].map((column, index) => (
              <div key={index} className="uncf-num flex h-full w-16 flex-col items-center justify-end gap-1.5 text-[15px]">
                {one(column.value)}
                <div className="w-full rounded-t-[3px]" style={{ height: `${((column.value ?? 0) / top) * 100}%`, background: column.color }} />
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="flex justify-around pt-2 text-center text-(--uncf-ink-2)">
        {data.terms.map((term) => (
          <span key={term.label}>
            {term.label}
            <span className="block text-[13px] text-(--uncf-ink-3)">{formatCount(term.enrolled)} enrolled</span>
          </span>
        ))}
      </div>
    </Card>
  );
}

/** Students grouped by credits earned in year 1, and how many of each group were retained. */
function TiersCard({ data }: { data: CreditsResponse }) {
  const shownTiers = data.tiers.filter((tier) => tier.share !== null);
  const words = retentionWords(data.meta.retention_type, data.meta.retention_term);
  return (
    <Card>
      <CardHead
        title={`Credit tiers and retention (${words.lower})`}
        subtitle="Students grouped by credits earned in year 1. Students who earn more credits come back at higher rates."
      />
      <div className="mt-5 mb-6.5 flex h-12.5 overflow-hidden rounded font-semibold" role="img" aria-label={shownTiers.map((t) => `${t.label}: ${formatShare(t.share)}`).join(", ")}>
        {shownTiers.map((tier) => (
          <div
            key={tier.key}
            className="flex items-center overflow-hidden px-4 whitespace-nowrap"
            style={{ flex: tier.share!, background: tierStyle[tier.key].fill, color: tierStyle[tier.key].text }}
            title={`${tier.label} · ${formatShare(tier.share)}`}
          >
            {/* A narrow part, or any part on a phone, only has room for its share; the table below names it. */}
            {tier.share! >= 0.15 && <span className="max-sm:hidden">{tier.label} · </span>}
            {formatShare(tier.share)}
          </div>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className={cn(tableClasses.table, "min-w-120")}>
          <thead>
            <tr>
              <th className={tableClasses.th}>Credits earned, year 1</th>
              <th className={cn(tableClasses.th, tableClasses.right, "pr-8")}>Students</th>
              <th className={tableClasses.th}>{words.name}</th>
              <th className={tableClasses.th} />
            </tr>
          </thead>
          <tbody>
            {data.tiers.map((tier) => (
              <tr key={tier.key}>
                <td className={tableClasses.td}>{tier.label}</td>
                <td className={cn(tableClasses.td, tableClasses.right, "uncf-num pr-8")}>{formatCount(tier.students)}</td>
                <td className={cn(tableClasses.td, "w-[60%]")}>
                  <TrackBar share={tier.rate} color={tierStyle[tier.key].bar} height={12} label={`${tier.label}: ${formatShare(tier.rate)} retained`} />
                </td>
                <td className={cn(tableClasses.td, tableClasses.right, "uncf-num pl-4")}>{formatShare(tier.rate)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Counted>
        credits are the cohort file’s year-1 credits attempted and earned: every term of the student’s first academic year
        {data.credits!.left_out ? `; ${fmt(data.credits!.left_out)} students with blank credits are left out` : ""}. The
        by-term columns use the course file’s credits for the starting term and the next fall or spring term.{" "}
        {words.name}: {words.how}. The credit completion ratio counts first-time and
        transfer-in students who attempted at least one credit. Tiers with fewer than 10 students are hidden.
      </Counted>
    </Card>
  );
}
