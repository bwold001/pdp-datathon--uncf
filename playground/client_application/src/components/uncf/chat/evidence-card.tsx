"use client";

import { useState } from "react";
import type { Payload, Rate, Receipt, Status } from "@/services/student-success-v2";
import { Button } from "@/components/ui/button";

const statuses: Record<Status, string> = {
  ok: "Available", provisional: "Provisional — follow-up is incomplete", unknown: "Unknown — no observed value",
  unavailable: "Unavailable — required evidence is missing", not_yet_observable: "Not yet observable — follow-up is incomplete",
  not_reported: "Not reported by the source", suppressed: "Historical suppressed receipt — omitted values require recomputation",
};

/** Format only serialized numerical inputs, preserving negative values and valid zeros. */
function RateValue({ value }: { value: Rate }) {
  return <div><p className="text-lg font-semibold">{(value.value * 100).toFixed(2)}%</p>
    <p>{value.numerator} {value.numerator_unit} / {value.denominator} {value.denominator_unit}</p>
    {value.n_students != null && <p>Distinct students n={value.n_students}</p>}
    {value.n_excluded != null && <p>Excluded: {value.n_excluded}</p>}
    {value.n_out_of_scope != null && <p>Out of scope: {value.n_out_of_scope}</p>}
    {value.split && <p>{Object.entries(value.split).map(([key, n]) => `${key}: ${n}`).join(" · ")}</p>}
  </div>;
}

/** Navigate immutable receipt pages; changing pages never recomputes evidence. */
function EvidenceTable({ payload }: { payload: Extract<Payload, { kind: "table" }> }) {
  const [page, setPage] = useState(0);
  const pages = [payload.rows, ...(payload.pages ?? []).map((p) => p.rows)];
  return <div className="overflow-x-auto">
    {pages.length > 1 && <nav aria-label="Evidence pages" className="flex items-center gap-3 py-2">
      <Button variant="outline" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous evidence page</Button>
      <span>Page {page + 1} of {pages.length} · {pages.reduce((n, rows) => n + rows.length, 0)} rows</span>
      <Button variant="outline" disabled={page === pages.length - 1} onClick={() => setPage(page + 1)}>Next evidence page</Button>
    </nav>}
    <table className="w-full text-left text-sm"><thead><tr>{payload.columns.map((c) => <th key={c.id} className="border p-2">{c.id} ({c.unit})</th>)}<th className="border p-2">Status</th></tr></thead>
      <tbody>{pages[page].map((row, index) => <tr key={index}>{row.cells ? row.cells.map((cell, i) => <td key={i} className="border p-2">{cell === null ? "Unknown / no observed value" : cell}</td>) : <td className="border p-2" colSpan={payload.columns.length}>{row.path ?? "Result"}</td>}<td className="border p-2">{statuses[row.status]}</td></tr>)}</tbody>
    </table>
  </div>;
}

/** Render every typed payload using its own units and applicable sample sizes. */
export function Evidence({ payload }: { payload: Payload }) {
  switch (payload.kind) {
    case "count": return <p>{payload.count} {payload.unit}</p>;
    case "mean": return <p>Mean: {payload.value} {payload.unit} · n={payload.n}</p>;
    case "correlation": return <p>Pearson r={payload.coefficient} · paired n={payload.n} · x: {payload.x_unit}; y: {payload.y_unit}</p>;
    case "mean_comparison": return <div>{payload.groups.map((g) => <p key={g.id}>{g.id}: {g.mean} {payload.unit} · n={g.n}</p>)}{payload.differences.map((d) => <p key={`${d.minuend}-${d.subtrahend}`}>{d.minuend} − {d.subtrahend}: {d.value} {payload.unit}</p>)}</div>;
    case "table": return <EvidenceTable payload={payload} />;
    case "rate": return <div><RateValue value={payload} />{payload.breakdowns.map((row, i) => <div key={i} className="mt-3 rounded border p-2"><p>{Object.entries(row.group).filter(([, v]) => v !== null).map(([k, v]) => `${k}: ${v}`).join(" · ")}</p>{(row.status === "ok" || row.status === "provisional") && row.value !== undefined ? <RateValue value={row as Rate} /> : <p>{statuses[row.status]}</p>}{row.exclusions?.map((e) => <p key={e.reason}>Excluded {e.reason}: {e.count}</p>)}</div>)}</div>;
  }
}

/** Display source identity, exact executed scope and versioned evidence together. */
export function EvidenceCard({ receipt }: { receipt: Receipt }) {
  return <article className="min-w-0 space-y-3 rounded-xl border bg-card p-4 text-sm">
    <h3 className="font-semibold">{receipt.step_id} · {receipt.operation_id}</h3>
    <p>{statuses[receipt.result.status]}</p>
    {receipt.result.payload && <Evidence payload={receipt.result.payload} />}
    {receipt.result.exclusions?.map((e) => <p key={e.reason}>Excluded {e.reason}: {e.count}</p>)}
    <p>Population: {receipt.population} · Grain: {receipt.grain} · Window: {receipt.time_window}</p>
    <details><summary>Scope, definitions and source</summary><dl className="space-y-2 break-all">
      {[
        ["Executed parameters and filters", JSON.stringify(receipt.request.parameters)],
        ["Result policy", receipt.disclosure_profile ? `${receipt.disclosure_profile.id} v${receipt.disclosure_profile.version}` : receipt.versions.disclosure],
        ["Definitions", receipt.definitions.map((d) => `${d.id} v${d.version}`).join(", ")],
        ["Source loaded", receipt.source.loaded_at], ["Coverage", receipt.source.coverage],
        ["Snapshot", receipt.source.snapshot_ref], ["Source fingerprint", receipt.source.fingerprint],
        ["Versions (pipeline, build, configuration, policy)", JSON.stringify(receipt.versions)],
        ["Computation fingerprint", receipt.computation_fingerprint], ["Execution", receipt.execution_id],
        ["Started", receipt.started_at], ["Completed", receipt.completed_at],
      ].map(([label, value]) => <div key={label}><dt className="font-medium">{label}</dt><dd>{value}</dd></div>)}
    </dl></details>
    {[...receipt.assumptions, ...receipt.limitations, ...receipt.baseline_changes].map((note, i) => <p key={i}>{note}</p>)}
    <p className="text-xs text-muted-foreground">Synthetic demonstration data. These are not findings about real students or institutions.</p>
  </article>;
}
