import type { Metadata } from "next";

import { DataChat } from "@/components/chat/data-chat";
import { PageIntro } from "@/components/page-intro";
import { SectionHeading } from "@/components/section-heading";

export const metadata: Metadata = {
  title: "Chat UI with an LLM over data",
  description: "The Chat UI's side panel, answered by an LLM over the PDP data model.",
};

export default function DataChatUiPage() {
  return (
    <>
      <PageIntro eyebrow="Sandbox" title="Chat UI with an LLM over data">
        <p>
          The Chat UI&apos;s side panel, with real answers. An LLM follows the metadata-advisor skill, reads the data
          model&apos;s definitions, and runs read-only aggregate queries that only return groups of 10 or more students.
        </p>
        <p>
          It never sees student records. The data in this repository is synthetic: nothing here is a finding about real
          students or institutions.
        </p>
      </PageIntro>

      <section aria-labelledby="data-chat-heading" className="flex flex-col gap-6">
        <SectionHeading id="data-chat-heading" title="Ask the data">
          <p className="text-muted-foreground">
            Needs <code className="font-mono text-sm">ANTHROPIC_API_KEY</code> in the server&apos;s{" "}
            <code className="font-mono text-sm">.env.development.local</code>. For counts, load the data model from the
            pipeline page first.
          </p>
        </SectionHeading>
        <div className="mx-auto h-[44rem] w-full max-w-4xl overflow-hidden rounded-2xl border bg-card shadow-sm">
          <DataChat />
        </div>
      </section>
    </>
  );
}
