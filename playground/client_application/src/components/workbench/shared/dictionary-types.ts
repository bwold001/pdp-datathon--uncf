/** Generic item identifiers are supplied by callers. */
export type DescribedItem = { id: string; label: string; description: string };

export type DictionaryValue = { code: string; meaning: string };

/** Optional profile supplied by the caller, independently of dictionary metadata. */
export type FieldProfile = {
  fillPercent: number;
  distinctCount: number;
  totalRows: number;
  topValues: { value: string; count: number }[];
};

export type FieldDefinition = {
  id: string;
  title: string;
  description: string;
  source: string;
  values?: DictionaryValue[];
  profile?: FieldProfile;
};

/** A dictionary field with its table and source-file grouping. */
export type GuideField = FieldDefinition & { group: string; file: string; notInData?: boolean };
