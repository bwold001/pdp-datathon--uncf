"use client";

import { useMemo, useState } from "react";

import { LoadError } from "@/components/load-error";
import { FieldGuidePage } from "@/components/workbench/field-guide/field-guide-page";
import { Spinner } from "@/components/ui/spinner";
import { toIndexSections } from "@/services/workbench-mappers";
import { useWorkbenchData } from "@/app/(dashboard)/workbench/workbench-data";

const ALL = "All";

/** The field guide over the data model's column dictionary, with search, grouping and selection. */
export function FieldGuide() {
  const { columns, fields, retryColumns, hasData } = useWorkbenchData();
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState(ALL);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const groups = useMemo(
    () => [ALL, ...new Set(fields.map((field) => field.group))].map((label) => ({ id: label, label })),
    [fields],
  );
  const matching = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return fields.filter(
      (field) =>
        (group === ALL || field.group === group) &&
        `${field.title} ${field.id} ${field.description}`.toLowerCase().includes(needle),
    );
  }, [fields, group, query]);

  if (columns.status === "loading") {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Spinner aria-hidden />
        Loading the field guide…
      </p>
    );
  }
  if (columns.status === "error") {
    return <LoadError title="The field guide couldn't load." message={columns.message} onRetry={retryColumns} />;
  }

  const selected = matching.find((field) => field.id === selectedId) ?? matching[0];
  const sections = toIndexSections(matching);
  return (
    <FieldGuidePage
      search={{ value: query, onValueChange: setQuery }}
      groups={{ groups, value: group, onValueChange: setGroup }}
      index={{ sections, selectedId: selected?.id ?? null, onSelect: setSelectedId }}
      detail={{ field: selected, profileSource: hasData ? "uploaded" : "mock" }}
    />
  );
}
