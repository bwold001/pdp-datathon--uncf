"use client";

import { QuestionComposer, SuggestedQuestions } from "@/components/chat/panel-chat";
import { Button } from "@/components/ui/button";
import { useUncfChat } from "@/hooks/use-uncf-chat";
import { useScrollToLatest } from "@/hooks/use-scroll-to-latest";
import { sendUncfQuestion } from "@/services/uncf-chat";
import { CalculationCard } from "./calculation-card";

const questions = [
  "What is the graduation rate for chemistry majors?",
  "What is the retention rate for all majors?",
  "What is enrollment ethnicity by academic program over the past 2 years?",
];

/** Staff questions with explicit clarifications and inspectable calculation evidence. */
export function UncfChat({ request = sendUncfQuestion }: { request?: typeof sendUncfQuestion }) {
  const { messages, pending, clarification, revision, ask, select, reset } = useUncfChat(request);
  const scrollRef = useScrollToLatest<HTMLDivElement>(`${messages.length}:${pending}`);
  return (
    <section aria-label="Student success chat" className="flex h-full min-h-0 min-w-0 flex-col">
      <header className="flex items-center justify-between gap-3 border-b p-4">
        <div><h2 className="font-semibold">Ask about student success</h2><p className="text-sm text-muted-foreground">Answers with definitions, supporting counts and calculations.</p></div>
        <Button variant="outline" onClick={reset}>Start over</Button>
      </header>
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="space-y-4 py-6"><p>Ask about graduation, retention or enrollment. I’ll ask for any details that change the answer.</p><SuggestedQuestions questions={questions} onQuestionChosen={ask} /></div>
        ) : (
          <ol className="space-y-5" aria-label="Conversation">
            {messages.map((message) => (
              <li key={message.id} className="min-w-0 break-words">
                {message.role === "user" && <p className="ml-auto w-fit max-w-full rounded-xl bg-muted px-4 py-3">{message.text}</p>}
                {message.role === "error" && <p role="alert" className="rounded-lg border border-destructive/40 p-3 text-destructive">{message.text}</p>}
                {message.role === "assistant" && <div className="space-y-3"><p>{message.answer.message}</p>{message.answer.receipts.map((receipt, index) => <CalculationCard key={index} receipt={receipt} />)}</div>}
              </li>
            ))}
          </ol>
        )}
        {pending && <p role="status" className="mt-4 text-sm text-muted-foreground">Looking up the approved calculations…</p>}
        {clarification && <fieldset disabled={pending} className="mt-4 space-y-2"><legend className="font-medium">{clarification.message}</legend><div className="flex flex-wrap gap-2">{clarification.choices.map((choice) => <Button key={choice.value} variant="outline" className="h-auto whitespace-normal py-2 text-left" onClick={() => select(choice.value)}>{choice.label}</Button>)}</div>{clarification.choices.length === 0 && <p>No choices are available. Check that the normalized data has been loaded.</p>}</fieldset>}
      </div>
      <QuestionComposer key={revision} onSubmit={ask} disabled={pending} placeholder="Ask a student success question…" />
      <p className="px-4 pb-3 text-xs text-muted-foreground">Synthetic demonstration. Each new question starts a separate analysis.</p>
    </section>
  );
}
