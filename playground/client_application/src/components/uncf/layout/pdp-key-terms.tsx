"use client";

import { useMemo } from "react";

import { useApiResource } from "@/hooks/use-api-resource";

import { explorerLoader } from "./explorer-api";

/** One measure's definition from the shared dictionary (measures/definitions.py). */
export type PdpDefinition = { name: string; pdp_name: string; what: string; how: string; who: string; limits: string[] };

/** The answer from GET /uncf/definitions. */
export type DefinitionsResponse = { definitions: Record<string, PdpDefinition> };

type PdpKeyTermsProps = {
  /** The measures to define, e.g. ["retention", "persistence"], in this order. */
  terms: string[];
  /** Terms the dictionary doesn't have, written by the tab, shown after the dictionary's. */
  children?: React.ReactNode;
};

/**
 * Key terms for a tab, in the shared dictionary's words: the same definitions the Results API sends, so every page
 * says the same thing. Edit the wording in measures/definitions.py, not here.
 */
export function PdpKeyTerms({ terms, children }: PdpKeyTermsProps) {
  const load = useMemo(() => explorerLoader<DefinitionsResponse>("/uncf/definitions", ""), []);
  const { resource } = useApiResource(load);
  return <PdpKeyTermsView terms={terms} definitions={resource.status === "success" ? resource.data.definitions : undefined} failed={resource.status === "error"}>{children}</PdpKeyTermsView>;
}

type PdpKeyTermsViewProps = PdpKeyTermsProps & {
  /** The dictionary, or undefined while it loads. */
  definitions?: Record<string, PdpDefinition>;
  failed?: boolean;
};

/** The key terms drawn from a loaded dictionary. */
export function PdpKeyTermsView({ terms, definitions, failed, children }: PdpKeyTermsViewProps) {
  return (
    <>
      {definitions === undefined ? (
        <span className="text-(--uncf-ink-3)">{failed ? "The definitions couldn’t load." : "Loading definitions…"}</span>
      ) : (
        terms
          .filter((term) => definitions[term])
          .map((term) => (
            <span key={term}>
              <b className="font-semibold">{definitions[term].name}</b> (PDP {definitions[term].pdp_name}):{" "}
              {lowerFirst(definitions[term].what)}{" "}
            </span>
          ))
      )}
      {children}
    </>
  );
}

/** The sentence with its first letter in lower case, to follow a colon. */
function lowerFirst(text: string): string {
  return text.charAt(0).toLowerCase() + text.slice(1);
}
