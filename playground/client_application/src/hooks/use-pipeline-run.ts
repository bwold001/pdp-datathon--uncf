"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError } from "@/lib/api-client";
import { describeError } from "@/lib/errors";
import { getRun, startRun, type RunRequest, type RunStatus } from "@/services/workbench";

const POLL_INTERVAL_MS = 1_000;
// A full mock load takes well under a minute; past this, something is stuck.
const MAX_POLLS = 600;

export type PipelineRunState =
  | { status: "idle" }
  | { status: "running"; run: RunStatus | null }
  | { status: "succeeded"; run: RunStatus }
  | { status: "failed"; message: string; run: RunStatus | null };

/** A load run's state and the functions that start and clear it. */
export type PipelineRun = {
  state: PipelineRunState;
  start: (request?: RunRequest) => Promise<PipelineRunState>;
  reset: () => void;
};

/** Wait between polls, or stop early when the caller has given up. */
function wait(milliseconds: number, signal: AbortSignal) {
  return new Promise<void>((resolve) => {
    /** Release the timer and abort listener when either one finishes the wait. */
    function finish() {
      clearTimeout(timer);
      signal.removeEventListener("abort", finish);
      resolve();
    }
    const timer = setTimeout(finish, milliseconds);
    signal.addEventListener("abort", finish, { once: true });
    if (signal.aborted) finish();
  });
}

/** Start a load run and poll it until it ends. `start` resolves with how the run ended. */
export function usePipelineRun(): PipelineRun {
  const [state, setState] = useState<PipelineRunState>({ status: "idle" });
  const controller = useRef<AbortController | null>(null);

  useEffect(() => () => controller.current?.abort(), []);

  const start = useCallback(async (request: RunRequest = {}): Promise<PipelineRunState> => {
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    const settle = (next: PipelineRunState) => {
      if (!abort.signal.aborted) setState(next);
      return next;
    };

    settle({ status: "running", run: null });
    try {
      let run = await startRun(request, abort.signal);
      for (let poll = 0; run.status === "running"; poll++) {
        if (poll >= MAX_POLLS) {
          return settle({ status: "failed", message: "The load is taking too long. Check the server log, then try again.", run });
        }
        settle({ status: "running", run });
        await wait(POLL_INTERVAL_MS, abort.signal);
        if (abort.signal.aborted) return { status: "idle" };
        run = await getRun(run.run_id, abort.signal);
      }
      if (run.status === "succeeded") return settle({ status: "succeeded", run });
      return settle({ status: "failed", message: run.error ?? "The load failed.", run });
    } catch (error) {
      if (abort.signal.aborted) return { status: "idle" };
      const lost = error instanceof ApiError && error.status === 404;
      const message = lost ? "The server lost track of the load, likely because it restarted. Try again." : describeError(error);
      return settle({ status: "failed", message, run: null });
    }
  }, []);

  const reset = useCallback(() => {
    controller.current?.abort();
    setState({ status: "idle" });
  }, []);

  return { state, start, reset };
}
