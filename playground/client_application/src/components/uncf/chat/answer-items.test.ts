import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { Payload, Receipt, TableRow } from "@/services/student-success-v2";
import { chatAnswerItems } from "./answer-items";
import { EvidenceCard } from "./evidence-card";

/** Build a complete synthetic receipt for chat rendering without a server or provider. */
function receiptFor(operation: string, payload: Payload): Receipt {
  return {
    schema_version: 2, step_id: "answer", operation_id: operation, operation_version: "1",
    request: { kind: "defined_measure", operation_id: operation, step_id: "answer", depends_on: [], parameters: { cohort: "2023-24" } },
    population: "Synthetic cohort", grain: "students", time_window: "year one", definitions: [],
    assumptions: [], limitations: [], baseline_changes: [],
    source: { label: "synthetic", snapshot_ref: "a".repeat(64), fingerprint: "b".repeat(64), loaded_at: "2026-11-11", coverage: "Fixture" },
    versions: { catalog: "2", pipeline: "test", configuration: "test", coverage: "test", implementation: "test", disclosure: "2", features: [] },
    computation_fingerprint: "c".repeat(64), execution_id: "test", started_at: "2026-11-11T00:00:00Z", completed_at: "2026-11-11T00:00:01Z",
    presentation: { title: "Results", scope: "Synthetic cohort", summary: "Results are shown below.", items: [], caveats: [] },
    result: { status: "ok", payload },
  };
}

const grouped: Payload = {
  kind: "table",
  columns: ["group", "count", "earned_mean", "earned_n", "earned_missing", "attempted_mean", "attempted_n", "attempted_missing"].map((id) => ({ id, type: id === "group" ? "text" : "number", unit: "fixture" })),
  rows: [{ status: "ok", cells: ["zero", 3, 0, 2, 1, 20, 3, 0] }],
  pages: [{ rows: [{ status: "ok", cells: ["one_to_two", 1, null, 0, 1, 12, 1, 0] }] }],
};

test("group summaries retain zero, independent samples, missing means and later pages", () => {
  const receipt = receiptFor("grouped_summary", grouped);
  const original = JSON.stringify(receipt);
  assert.deepEqual(chatAnswerItems(receipt), [
    "0 observed online enrollments — average first-year credits earned: 0 credits (usable n=2; missing=1).",
    "0 observed online enrollments — average first-year credits attempted: 20 credits (usable n=3; missing=0).",
    "1–2 observed online enrollments — average first-year credits earned: Unavailable — no observed credits (usable n=0; missing=1).",
    "1–2 observed online enrollments — average first-year credits attempted: 12 credits (usable n=1; missing=0).",
  ]);
  assert.equal(JSON.stringify(receipt), original);
  const html = renderToStaticMarkup(createElement(EvidenceCard, { receipt }));
  assert.match(html, /earned: 0 credits/);
  assert.match(html, /<details>/);
  assert.doesNotMatch(html, /<details open=""/);
});

/** Build a hidden graduation row with its perspective, horizon and reason intact. */
function unavailable(label: string, kind: "rate" | "composition" = "rate", horizon: "four_year" | "six_year" = "four_year"): TableRow {
  return { status: "unavailable", explanation: { label, kind, horizon, reason: "completion_program_missing", note: null } };
}

test("graduation labels distinguish perspectives, kinds and horizons while preserving available rates", () => {
  const receipt = receiptFor("legacy.graduation", {
    kind: "table",
    columns: ["label", "kind", "horizon", "group", "numerator", "denominator", "count", "rate", "note"].map((id) => ({ id, type: "text", unit: "fixture" })),
    rows: [
      { status: "ok", cells: ["Entrants completing in any program", "rate", "four_year", "overall", 0, 2, null, 0, null] },
      unavailable("Entrants completing in the selected program"),
      unavailable("Entrants completing in the selected program"),
      unavailable("Program graduates who switched in", "composition"),
      unavailable("Entrants completing in the selected program", "rate", "six_year"),
    ],
  });
  const original = JSON.stringify(receipt);
  const items = chatAnswerItems(receipt);
  assert.equal(items.length, 4);
  assert.equal(items[0], "Within four years — Entrants completing in any program: 0.00% (0 of 2 students).");
  assert.match(items[1], /^Within four years — Entrants completing in the selected program:/);
  assert.match(items[2], /^Within four years — Program graduates who switched in:/);
  assert.match(items[3], /^Within six years — Entrants completing in the selected program:/);
  assert.equal(JSON.stringify(receipt), original);
});

for (const operation of ["student_paths.summary", "dfw.course_list", "gateway.course_outcomes", "credit_momentum.summary"]) {
  test(`${operation} chat table is initially open when no summary is supplied`, () => {
    const receipt = receiptFor(operation, { kind: "table", columns: [{ id: "number", type: "number", unit: "students" }], rows: [{ status: "ok", cells: [7] }] });
    const original = JSON.stringify(receipt);
    const html = renderToStaticMarkup(createElement(EvidenceCard, { receipt }));
    assert.match(html, /<details open="">/);
    assert.match(html, /<td class="border p-2">7<\/td>/);
    assert.equal(JSON.stringify(receipt), original);
  });
}

test("other operations preserve the supplied summary", () => {
  const receipt = receiptFor("dfw.rate", { kind: "count", count: 0, unit: "students" });
  receipt.presentation!.items = ["A supplied summary"];
  assert.deepEqual(chatAnswerItems(receipt), ["A supplied summary"]);
});
