"use client";

import { DatabaseZap, RotateCw } from "lucide-react";

import { QuestionComposer, SuggestedQuestions } from "@/components/chat/panel-chat";
import { EmptyState } from "@/components/empty-state";
import { Markdown } from "@/components/markdown";
import { QuestionBubble } from "@/components/question-bubble";
import { Button } from "@/components/ui/button";
import {
  DATA_CHAT_DESCRIPTION,
  DATA_CHAT_PLACEHOLDER,
  DATA_CHAT_SYNTHETIC_NOTE,
  DATA_CHAT_TITLE,
  DATA_CHAT_WELCOME,
  dataChatSuggestedQuestions,
} from "@/content/data-chat-ui";
import { type DataChatMessage, useDataChat } from "@/hooks/use-data-chat";
import { useScrollToLatest } from "@/hooks/use-scroll-to-latest";
import type { DataChatAnswer, ToolResult } from "@/services/data-chat";

/** PanelChat's layout, answered by an LLM over the data model: markdown replies and the tool results behind them. */
export function DataChat() {
  const { chatMessages, isAwaitingReply, submitQuestion, startNewChat } = useDataChat();
  const conversationRef = useScrollToLatest<HTMLDivElement>(chatMessages.length + Number(isAwaitingReply));

  return (
    <section aria-label={DATA_CHAT_TITLE} className="flex h-full min-h-0 flex-col">
      <header className="flex items-center justify-between gap-3 border-b px-5 py-4">
        <div className="min-w-0">
          <h2 className="font-semibold tracking-tight">{DATA_CHAT_TITLE}</h2>
          <p className="text-sm text-muted-foreground">{DATA_CHAT_DESCRIPTION}</p>
        </div>
        <Button variant="outline" size="icon" aria-label="Start over" title="Start over" onClick={startNewChat}>
          <RotateCw />
        </Button>
      </header>

      <div ref={conversationRef} className="min-h-0 flex-1 overflow-y-auto px-5 py-6">
        {chatMessages.length === 0 ? (
          <EmptyState
            icon={DatabaseZap}
            title="Ask the data"
            description={DATA_CHAT_WELCOME}
            bordered={false}
            className="h-full p-0"
          >
            <SuggestedQuestions questions={dataChatSuggestedQuestions} onQuestionChosen={submitQuestion} />
          </EmptyState>
        ) : (
          <ol className="flex flex-col gap-6">
            {chatMessages.map((message) => (
              <li key={message.id}>
                <DataChatMessageItem message={message} />
              </li>
            ))}
            {isAwaitingReply && (
              <li className="flex items-center gap-2 text-sm text-muted-foreground" aria-live="polite">
                <span className="size-1.5 rounded-full bg-muted-foreground motion-safe:animate-pulse" />
                Looking it up… this can take up to a minute.
              </li>
            )}
          </ol>
        )}
      </div>

      <QuestionComposer onSubmit={submitQuestion} disabled={isAwaitingReply} placeholder={DATA_CHAT_PLACEHOLDER} />
    </section>
  );
}

/** One turn: the question, the assistant's answer, or why there's no answer. */
function DataChatMessageItem({ message }: { message: DataChatMessage }) {
  if (message.role === "user") return <QuestionBubble>{message.text}</QuestionBubble>;
  if (message.role === "error") {
    return (
      <p role="alert" className="rounded-xl border border-destructive/40 px-4 py-3 text-sm text-destructive">
        {message.text}
      </p>
    );
  }
  return <AnswerView answer={message.answer} />;
}

/** The answer as markdown, then the tool results it came from. */
function AnswerView({ answer }: { answer: DataChatAnswer }) {
  return (
    <div className="flex flex-col gap-4">
      <Markdown>{answer.message}</Markdown>
      {answer.query && <ToolResultView label="Query" result={answer.query} />}
      {answer.definitions && <ToolResultView label="Definitions" result={answer.definitions} />}
      <p className="text-xs text-muted-foreground">
        {answer.tools_used.length > 0 ? `Tools used: ${answer.tools_used.join(", ")}. ` : "No tools used. "}
        {DATA_CHAT_SYNTHETIC_NOTE}
      </p>
    </div>
  );
}

/** One tool call, collapsed: the SQL it ran, if any, then its result as JSON. */
function ToolResultView({ label, result }: { label: string; result: ToolResult }) {
  const sql = typeof result.input.sql === "string" ? result.input.sql : null;
  return (
    <details className="rounded-lg border px-3 py-2 text-sm">
      <summary className="cursor-pointer font-medium">
        {result.is_error ? `${label} failed` : label}: {result.tool}
      </summary>
      {sql && <pre className="mt-2 overflow-x-auto rounded-lg bg-muted p-3 font-mono text-xs">{sql}</pre>}
      <pre className="mt-2 max-h-80 overflow-auto rounded-lg bg-muted p-3 font-mono text-xs">
        {JSON.stringify(result.output, null, 2)}
      </pre>
    </details>
  );
}
