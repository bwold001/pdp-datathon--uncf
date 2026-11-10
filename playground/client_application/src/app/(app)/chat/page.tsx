import { env } from "@/lib/env";
import type { Metadata } from "next";
import { StudentSuccessChat } from "@/components/chat/student-success/chat";

export const metadata: Metadata = { title: "Student success chat" };

/** Bounded chat demonstration over the team's shared analytics service. */
export default function StudentSuccessChatPage() {
  if (!env.studentSuccessChatEnabled) return <section>
    <h1 className="text-2xl font-semibold">Student success chat</h1>
    <p>Chat is not enabled on this site. Use your organization&apos;s Playground deployment.</p>
  </section>;
  return <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
    <div><p className="text-sm text-muted-foreground">UNCF · Student Success Explorer</p><h1 className="text-2xl font-semibold">Student success chat</h1><p className="mt-2 text-muted-foreground">Explore graduation, retention and enrollment, and see how each result was calculated.</p></div>
    <div className="h-[44rem] min-h-0 overflow-hidden rounded-2xl border bg-card"><StudentSuccessChat /></div>
  </div>;
}
