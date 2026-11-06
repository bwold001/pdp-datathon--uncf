"use client";

import { SearchX } from "lucide-react";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

export type FieldIndexSection = { id: string; label: string; fields: { id: string; title: string; fillPercent?: number; notInData?: boolean }[] };

/** Shows grouped dictionary matches and emits the selected field ID. */
export function FieldIndex({ sections, selectedId, onSelect }: { sections: FieldIndexSection[]; selectedId?: string | null; onSelect: (id: string) => void }) {
  const populated = sections.filter((section) => section.fields.length > 0);
  return (
    <nav aria-label="Field index">
      <ScrollArea className="h-80 md:h-[32rem]">
        {populated.length === 0 ? (
          <EmptyState icon={SearchX} title="No fields match" description="Try another search or group." bordered={false} />
        ) : (
          <div className="flex flex-col gap-4 pr-3">
            {populated.map((section) => (
              <section key={section.id} className="flex flex-col gap-2">
                <h2 className="text-sm font-medium">{section.label}</h2>
                <ul className="flex flex-col gap-1">
                  {section.fields.map((field) => (
                    <li key={field.id}>
                      <Button variant={selectedId === field.id ? "secondary" : "ghost"} aria-current={selectedId === field.id ? "true" : undefined} onClick={() => onSelect(field.id)} className="h-auto w-full justify-between gap-3 whitespace-normal text-left">
                        <span className="min-w-0 break-words">{field.title}</span>
                        <span className="shrink-0 text-xs text-muted-foreground">
                          {field.notInData ? "not in data" : field.fillPercent === undefined ? "" : `${field.fillPercent.toLocaleString("en-US")}% filled`}
                        </span>
                      </Button>
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        )}
      </ScrollArea>
    </nav>
  );
}
