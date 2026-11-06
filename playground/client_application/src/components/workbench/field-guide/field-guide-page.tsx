"use client";

import type { ComponentProps } from "react";
import { PageIntro } from "@/components/page-intro";
import { FieldGuideArticle } from "@/components/workbench/field-guide/field-guide-article";
import { FieldIndex } from "@/components/workbench/field-guide/field-index";
import { FieldSearch } from "@/components/workbench/field-guide/field-search";
import { FieldGroupToggle } from "@/components/workbench/field-guide/field-group-toggle";

export type FieldGuidePageProps = {
  search: ComponentProps<typeof FieldSearch>;
  groups: ComponentProps<typeof FieldGroupToggle>;
  index: ComponentProps<typeof FieldIndex>;
  detail: ComponentProps<typeof FieldGuideArticle>;
};

/** Composes the field guide while the caller owns search, groups and selection. */
export function FieldGuidePage({ search, groups, index, detail }: FieldGuidePageProps) {
  return (
    <div className="flex min-w-0 flex-col gap-6">
      <PageIntro size="sm" title="Field guide">
        <p>Read dictionary definitions before or after loading data.</p>
      </PageIntro>
      <div className="flex flex-col gap-3">
        <FieldSearch {...search} />
        <FieldGroupToggle {...groups} />
      </div>
      <div className="grid min-w-0 gap-6 md:grid-cols-[minmax(0,18rem)_minmax(0,1fr)]">
        <FieldIndex {...index} />
        <FieldGuideArticle {...detail} />
      </div>
    </div>
  );
}
