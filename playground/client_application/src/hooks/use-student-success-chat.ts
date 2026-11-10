"use client";

import { useCallback, useRef, useState } from "react";
import { describeError } from "@/lib/errors";
import { type AnalysisRequest, type ChatRequest, type ChatResponse, type Clarification, sendStudentSuccessQuestion } from "@/services/student-success-chat";

export type UncfMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; answer: ChatResponse }
  | { id: string; role: "error"; text: string };

/** Keep display history locally, carrying only an unresolved typed request to the API. */
export function useStudentSuccessChat(request = sendStudentSuccessQuestion) {
  const [messages, setMessages] = useState<UncfMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [clarification, setClarification] = useState<Clarification | null>(null);
  const [proposals, setProposals] = useState<AnalysisRequest[]>([]);
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
      setProposals(answer.proposals ?? []);
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
    setProposals([]);
    setClarification(null);
    return send({ prompt });
  }, [send]);

  const select = useCallback((value: string) => {
    if (!clarification) return;
    const label = clarification.choices.find((choice) => choice.value === value)?.label ?? value;
    return send({ prompt: question.current, pending: clarification.pending, ...(proposals.length ? { proposals } : {}), selection: { field: clarification.field, value } }, label);
  }, [clarification, proposals, send]);

  const confirm = useCallback(() => {
    if (busy.current || clarification || !proposals.length) return;
    return send({ prompt: question.current, confirmed: proposals }, "Confirmed the described scope; no additional filters.");
  }, [clarification, proposals, send]);

  const reset = useCallback(() => {
    generation.current += 1;
    busy.current = false;
    question.current = "";
    setProposals([]);
    setPending(false);
    setClarification(null);
    setMessages([]);
    setRevision((value) => value + 1);
  }, []);

  return { messages, pending, clarification, revision, proposals, ask, select, confirm, reset };
}
