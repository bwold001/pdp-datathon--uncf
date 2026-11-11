"use client";

import { useCallback, useRef, useState } from "react";
import { describeError } from "@/lib/errors";
import { type ChatRequestV2, type ChatResponseV2, type Plan, sendStudentSuccessV2 } from "@/services/student-success-v2";

export type UncfMessage =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; answer: ChatResponseV2 }
  | { id: string; role: "error"; text: string };
export type ConversationState = "proposed" | "needs_clarification" | "ready_for_confirmation" | "executing" | "completed" | "failed";

/** Invalidate old requests on every new question and retain the entire review plan. */
export function useStudentSuccessChat(request = sendStudentSuccessV2) {
  const [messages, setMessages] = useState<UncfMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [answer, setAnswer] = useState<ChatResponseV2 | null>(null);
  const [state, setState] = useState<ConversationState>("proposed");
  const [revision, setRevision] = useState(0);
  const generation = useRef(0);
  const busy = useRef(false);
  const question = useRef("");

  const send = useCallback(async (payload: ChatRequestV2, displayText = payload.prompt) => {
    const current = ++generation.current;
    busy.current = true;
    setPending(true);
    setAnswer(null);
    setState(payload.confirmed ? "executing" : "proposed");
    setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "user", text: displayText }]);
    try {
      const response = await request(payload);
      if (generation.current !== current) return;
      setAnswer(response);
      setState(response.status === "clarification" ? "needs_clarification" : response.status === "confirmation" ? "ready_for_confirmation" : response.status === "answer" ? "completed" : "failed");
      setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "assistant", answer: response }]);
    } catch (error) {
      if (generation.current !== current) return;
      setState("failed");
      setMessages((previous) => [...previous, { id: crypto.randomUUID(), role: "error", text: describeError(error) }]);
    } finally {
      if (generation.current === current) { busy.current = false; setPending(false); }
    }
  }, [request]);

  const ask = useCallback((prompt: string) => {
    if (!prompt.trim()) return;
    question.current = prompt;
    return send({ protocol_version: 2, prompt });
  }, [send]);
  const select = useCallback((value: string | number) => {
    const ref = answer?.clarification;
    if (busy.current || !ref || !answer?.plan) return;
    return send({ protocol_version: 2, prompt: question.current, plan: answer.plan,
      selection: { step_id: ref.step_id, parameter: ref.parameter, value } }, ref.choices.find((c) => c.value === value)?.label ?? String(value));
  }, [answer, send]);
  const confirm = useCallback(() => {
    if (busy.current || answer?.status !== "confirmation" || answer.plan?.kind !== "executable") return;
    return send({ protocol_version: 2, prompt: question.current, confirmed: answer.plan }, "Confirmed the complete displayed scope.");
  }, [answer, send]);
  const reset = useCallback(() => {
    generation.current += 1;
    busy.current = false;
    question.current = "";
    setAnswer(null); setPending(false); setState("proposed"); setMessages([]);
    setRevision((value) => value + 1);
  }, []);
  const plan: Plan | null = answer?.plan ?? null;
  return { messages, pending, clarification: answer?.clarification ?? null, revision, plan, state, ask, select, confirm, reset };
}
