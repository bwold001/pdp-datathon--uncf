"use client";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

export type FieldGroup = { id: string; label: string };

/** Emits a single dictionary-group selection without filtering the data itself. */
export function FieldGroupToggle({ groups, value, onValueChange }: { groups: FieldGroup[]; value: string; onValueChange: (value: string) => void }) {
  return (
    <ToggleGroup aria-label="Field groups" multiple={false} value={[value]} onValueChange={(values) => {
      if (values.length > 0) onValueChange(values[0]);
    }} variant="outline" className="max-w-full flex-wrap">
      {groups.map((group) => (
        <ToggleGroupItem key={group.id} value={group.id}>{group.label}</ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}
