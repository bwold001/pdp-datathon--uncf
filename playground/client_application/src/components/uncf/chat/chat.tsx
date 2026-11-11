"use client";

import { useState } from "react";
import { QuestionComposer, SuggestedQuestions } from "@/components/chat/panel-chat";
import { Button } from "@/components/ui/button";
import { useStudentSuccessChat } from "@/hooks/use-student-success-chat";
import { useScrollToLatest } from "@/hooks/use-scroll-to-latest";
import { type Parameter, type Plan, sendStudentSuccessV2 } from "@/services/student-success-v2";
import { EvidenceCard } from "./evidence-card";

const questions = [
  "What is the graduation rate for chemistry majors?",
  "What is the retention rate for all majors?",
  "What is enrollment ethnicity by academic program over the past 2 years?",
];

/** Staff questions with explicit clarifications and inspectable calculation evidence. */
export function StudentSuccessChat({ request = sendStudentSuccessV2 }: { request?: typeof sendStudentSuccessV2 }) {
  const { messages, pending, clarification, revision, plan, state, ask, select, confirm, reset } = useStudentSuccessChat(request);
  const scrollRef = useScrollToLatest<HTMLDivElement>(`${messages.length}:${pending}`);
  return (
    <section data-state={state} aria-label="Student success chat" className="flex h-full min-h-0 min-w-0 flex-col">
      <header className="flex items-center justify-between gap-3 border-b p-4">
        <div><h2 className="font-semibold">Ask about student success</h2><p className="text-sm text-muted-foreground">Answers with definitions, supporting counts and calculations.</p></div>
        <Button variant="outline" onClick={reset}>Start over</Button>
      </header>
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="space-y-4 py-6"><p>Ask about defined student success measures, graduation or enrollment. I’ll ask for any details that change the answer.</p><SuggestedQuestions questions={questions} onQuestionChosen={ask} /></div>
        ) : (
          <ol className="space-y-5" aria-label="Conversation">
            {messages.map((message) => (
              <li key={message.id} className="min-w-0 break-words">
                {message.role === "user" && <p className="ml-auto w-fit max-w-full rounded-xl bg-muted px-4 py-3">{message.text}</p>}
                {message.role === "error" && <p role="alert" className="rounded-lg border border-destructive/40 p-3 text-destructive">{message.text}</p>}
                {message.role === "assistant" && <div className="space-y-3"><p>{message.answer.message}</p>{message.answer.outcome === "partial" && <p role="alert">Partial answer: some steps failed or were not executed.</p>}{message.answer.step_outcomes.filter((s) => s.outcome !== "completed").map((s) => <p key={s.step_id}>{s.step_id}: {s.outcome} — {s.issue?.message}</p>)}{message.answer.issues.map((issue, i) => <p key={i}>{issue.step_id ? `${issue.step_id}: ` : ""}{issue.message} ({issue.code})</p>)}{message.answer.receipts.map((receipt, index) => <EvidenceCard key={index} receipt={receipt} />)}</div>}
              </li>
            ))}
          </ol>
        )}
        {pending && <p role="status" className="mt-4 text-sm text-muted-foreground">Looking up the approved calculations…</p>}
        {clarification && <fieldset disabled={pending} className="mt-4 space-y-2"><legend className="font-medium">{clarification.step_id}: {clarification.question}</legend><div className="flex flex-wrap gap-2">{clarification.choices.map((choice) => <Button key={choice.value} variant="outline" className="h-auto whitespace-normal py-2 text-left" onClick={() => select(choice.value)}>{choice.label}</Button>)}</div>{clarification.choices.length === 0 && <p>No choices are available. Check that the normalized data has been loaded.</p>}</fieldset>}
        {plan && (state === "ready_for_confirmation" || state === "needs_clarification") && <ScopeConfirmation key={JSON.stringify(plan)} plan={plan}
          disabled={pending || state !== "ready_for_confirmation"} onConfirm={confirm} />}
      </div>
      <QuestionComposer key={revision} onSubmit={ask} disabled={false} placeholder="Ask a student success question…" />
      <p className="px-4 pb-3 text-xs text-muted-foreground">Synthetic demonstration. Each new question starts a separate analysis.</p>
    </section>
  );
}

/** Every numerical request needs an explicit, initially unchecked scope approval. */
function ScopeConfirmation({ plan, disabled, onConfirm }: {
  plan: Plan; disabled: boolean; onConfirm: () => void;
}) {
  const [accepted, setAccepted] = useState(false);
  return <fieldset disabled={disabled} className="mt-4 space-y-3 rounded-lg border p-4">
    <legend className="font-semibold">Confirm calculation scope</legend>
    <ul className="list-disc space-y-2 pl-5">{plan.steps.map((step) => <li key={step.step_id}><strong>{step.step_id}: {step.operation_id}</strong><dl className="mt-2 space-y-1">{Object.entries(step.parameters).map(([key, value]) => <div key={key}><dt className="font-medium">{key.replaceAll("_", " ")}</dt><dd>{describeParameter(value)}</dd></div>)}</dl>{step.depends_on.length > 0 && <p>Depends on: {step.depends_on.join(", ")}</p>}</li>)}</ul>
    <p>Only the displayed cohort, filters and definitions will be used. Check that every requested constraint is present.</p>
    {disabled && <p>Resolve the remaining clarification before confirming.</p>}
    <label className="flex items-start gap-2"><input type="checkbox" checked={accepted}
      onChange={(event) => setAccepted(event.target.checked)} />
      I confirm this scope matches my question.</label>
    <Button disabled={disabled || !accepted} onClick={onConfirm}>Confirm scope and calculate</Button>
  </fieldset>;
}

/** Show canonical scope values in staff language without inventing inherited context. */
function describeParameter(value: Parameter): string {
  if (typeof value === "string" || typeof value === "number") return String(value);
  if (Array.isArray(value)) return value.length ? value.join(", ") : "Overall (no breakdown)";
  if ("unresolved" in value && value.unresolved === true) return String(value.question);
  const selected = Object.entries(value).filter(([, item]) => item !== null);
  return selected.length ? selected.map(([key, item]) => `${key.replaceAll("_", " ")}: ${item}`).join(" · ") : "All eligible students (no categorical filters)";
}
