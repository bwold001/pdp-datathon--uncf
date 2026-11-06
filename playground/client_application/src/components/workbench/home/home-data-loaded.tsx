import { useId, type ComponentProps } from "react";
import { PageIntro } from "@/components/page-intro";
import { StatTile } from "@/components/stat-tile";
import { UploadStatusLine } from "@/components/workbench/home/upload-status-line";
import { StarterQuestionList } from "@/components/workbench/home/starter-question-list";

export type HomeStat = ComponentProps<typeof StatTile> & { id: string };
type HomeDataLoadedProps = {
  stats: HomeStat[];
  lastUpload: ComponentProps<typeof UploadStatusLine>;
  questions: ComponentProps<typeof StarterQuestionList>;
  children?: React.ReactNode;
};

/** Shows saved row counts, upload checks and questions to explore. */
export function HomeDataLoaded({ stats, lastUpload, questions, children }: HomeDataLoadedProps) {
  const headingId = useId();
  const intro: ComponentProps<typeof PageIntro> = {
    size: "sm", title: "Your data", children: <UploadStatusLine {...lastUpload} />,
  };
  return (
    <div className="flex max-w-5xl flex-col gap-6">
      <PageIntro {...intro} />
      <ul aria-label="What's in your files" className="grid gap-3 sm:grid-cols-3">
        {stats.map(({ id, ...stat }) => (
          <li key={id}>
            <StatTile {...stat} />
          </li>
        ))}
      </ul>
      {questions.questions.length > 0 && (
        <section aria-labelledby={headingId} className="flex flex-col gap-3">
          <h2 id={headingId} className="text-lg font-medium">Start with a question</h2>
          <StarterQuestionList {...questions} />
        </section>
      )}
      {children}
    </div>
  );
}
