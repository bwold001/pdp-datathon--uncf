/** The words the data chat says. Its replies come from an LLM over the data model, not canned text. */

export const DATA_CHAT_TITLE = "Data chat";
export const DATA_CHAT_DESCRIPTION = "Ask about the PDP data model. Answers use synthetic data.";
export const DATA_CHAT_WELCOME =
  "Ask what to look at, what a column means, or for a count. Answers come from the data model's definitions and aggregate queries.";
export const DATA_CHAT_PLACEHOLDER = "Ask about the data…";
export const DATA_CHAT_SYNTHETIC_NOTE = "Built on synthetic data: not a finding about real students or institutions.";

// The first runs an aggregate query, so it needs the data model loaded (Sandbox pipeline page).
// The last gets proposed outside datasets, named as such.
export const dataChatSuggestedQuestions = [
  "What's the first-year retention rate by first-term enrollment intensity?",
  "How do I analyze first-year student drop-off between fall and spring?",
  "What does gateway_math_status mean, and what are its codes?",
  "What outside data could we add to improve outreach to students?",
];
