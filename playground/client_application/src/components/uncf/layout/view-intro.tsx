import { ShareInsightButton } from "./share-insight-button";

type ViewIntroProps = {
  title: string;
  /** One sentence under the title: what the tab is about. */
  children: React.ReactNode;
  whatThisShows: React.ReactNode;
  howToRead: React.ReactNode;
  keyTerms: React.ReactNode;
};

/** The top of every tab: its title and lead with Share Insight beside them, then the "What this shows / How to read it / Key terms" strip. */
export function ViewIntro({ title, children, whatThisShows, howToRead, keyTerms }: ViewIntroProps) {
  const explainers = [
    { term: "What this shows", body: whatThisShows },
    { term: "How to read it", body: howToRead },
    { term: "Key terms", body: keyTerms },
  ];

  return (
    <div className="flex flex-col gap-7">
      <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:gap-8">
        <div>
          <h2 className="mb-1.5 text-[28px] font-bold tracking-[-0.015em] text-balance md:text-[34px]">{title}</h2>
          <p className="max-w-[70ch] text-[17px] text-(--uncf-ink-2)">{children}</p>
        </div>
        <ShareInsightButton name={title} />
      </div>
      <dl className="grid rounded-[10px] border border-(--uncf-line) bg-(--uncf-surface) md:grid-cols-3">
        {explainers.map(({ term, body }) => (
          <div
            key={term}
            className="min-w-0 border-t border-(--uncf-line) px-6 py-5.5 first:border-t-0 md:border-t-0 md:border-l md:first:border-l-0"
          >
            <dt className="mb-1.5 text-xs font-bold tracking-widest text-(--uncf-ink-2) uppercase">{term}</dt>
            <dd>{body}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
