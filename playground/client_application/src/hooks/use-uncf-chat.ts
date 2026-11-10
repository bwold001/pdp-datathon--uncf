"use client";

import { useCallback, useRef, useState } from "react";
import { describeError } from "@/lib/errors";
import { type ChatRequest, type ChatResponse, type Clarification, sendUncfQuestion } from "@/services/uncf-chat";

export type UncfMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; answer: ChatResponse }
  | { id: string; role: "error"; text: string };

/** Keep display history locally, carrying only an unresolved typed request to the API. */
export function useUncfChat(request = sendUncfQuestion) {
  const [messages, setMessages] = useState<UncfMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [clarification, setClarification] = useState<Clarification | null>(null);
  const [revision, setRevision] = useState(0);
  const generation = useRef(0);
  const busy = useRef(false);
  const question = useRef("");

  const send = useCallback(async (payload: ChatRequest, displayText = payload.prompt) => {
    if (busy.current || !payload.prompt.trim()) return;
    busy.current = true;
    const current = ++generation.current;
    setPending(true);
    setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "user", text: displayText }]);
    try {
      const answer = await request(payload);
      if (generation.current !== current) return;
      setClarification(answer.clarification);
      setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "assistant", answer }]);
    } catch (error) {
      if (generation.current !== current) return;
      setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "error", text: describeError(error) }]);
    } finally {
      if (generation.current === current) {
        busy.current = false;
        setPending(false);
      }
    }
  }, [request]);

  const ask = useCallback((prompt: string) => {
    if (busy.current) return;
    question.current = prompt;
    setClarification(null);
    return send({ prompt });
  }, [send]);

  const select = useCallback((value: string) => {
    if (!clarification) return;
    const label = clarification.choices.find((choice) => choice.value === value)?.label ?? value;
    return send({ prompt: question.current, pending: clarification.pending, selection: { field: clarification.field, value } }, label);
  }, [clarification, send]);

  const reset = useCallback(() => {
    generation.current += 1;
    busy.current = false;
    question.current = "";
    setPending(false);
    setClarification(null);
    setMessages([]);
    setRevision((value) => value + 1);
  }, []);

  return { messages, pending, clarification, revision, ask, select, reset };
}
