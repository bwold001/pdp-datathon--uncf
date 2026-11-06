/** Ask the server's /sandbox/chat endpoint a question. Mirrors server_application/app/sandbox/chat/schemas.py. */

import { apiRequest } from "@/lib/api-client";

export type ToolResult = {
  tool: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  is_error: boolean;
};

export type DataChatAnswer = {
  /** Markdown: paragraphs, lists, tables and fenced SQL. */
  message: string;
  definitions: ToolResult | null;
  /** The last aggregate query: only groups of 10 or more students. */
  query: ToolResult | null;
  tools_used: string[];
  source: "synthetic";
};

const DATA_CHAT_PATH = "/sandbox/chat/suggest";

// The model may take several rounds of tool calls, far longer than the default 10 seconds.
const DATA_CHAT_TIMEOUT_MS = 90_000;

/** The assistant's answer to one question. Throws ApiError when the server can't answer. */
export function sendDataChatQuestion(question: string): Promise<DataChatAnswer> {
  return apiRequest<DataChatAnswer>(DATA_CHAT_PATH, {
    method: "POST",
    json: { prompt: question },
    timeoutMs: DATA_CHAT_TIMEOUT_MS,
  });
}
