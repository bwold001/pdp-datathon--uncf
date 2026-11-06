"use client";

import { useCallback, useRef, useState } from "react";

import { describeError } from "@/lib/errors";
import { type DataChatAnswer, sendDataChatQuestion } from "@/services/data-chat";

export type DataChatMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; answer: DataChatAnswer }
  | { id: string; role: "error"; text: string };

/** The data chat's conversation: like useChat, but each reply is the server's answer or its error. */
export function useDataChat() {
  const [chatMessages, setChatMessages] = useState<DataChatMessage[]>([]);
  const [isAwaitingReply, setAwaitingReply] = useState(false);
  // Each question gets a number, so a reply is dropped if Start over came first.
  const latestQuestionNumber = useRef(0);

  const submitQuestion = useCallback(async (question: string) => {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;
    const questionNumber = ++latestQuestionNumber.current;
    setChatMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "user", text: trimmedQuestion }]);
    setAwaitingReply(true);

    const reply: DataChatMessage = await sendDataChatQuestion(trimmedQuestion)
      .then((answer) => ({ id: crypto.randomUUID(), role: "assistant" as const, answer }))
      .catch((error: unknown) => ({ id: crypto.randomUUID(), role: "error" as const, text: describeError(error) }));
    if (questionNumber !== latestQuestionNumber.current) return;
    setAwaitingReply(false);
    setChatMessages((previous) => [...previous, reply]);
  }, []);

  const startNewChat = useCallback(() => {
    latestQuestionNumber.current += 1;
    setAwaitingReply(false);
    setChatMessages([]);
  }, []);

  return { chatMessages, isAwaitingReply, submitQuestion, startNewChat };
}
