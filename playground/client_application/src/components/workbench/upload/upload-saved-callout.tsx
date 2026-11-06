import { Fragment } from "react";
import Link from "next/link";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";

export type SavedTable = {
  name: string;
  rowCount: number;
};

type UploadSavedCalloutProps = {
  tables: SavedTable[];
  /** The columns the tables are linked on, such as "Student ID + Cohort". */
  joinKey?: string;
  /** Where "Explore the data" goes. */
  exploreHref: string;
  /** Anything else that was loaded with the files, such as enrichment tables. */
  children?: React.ReactNode;
};

const listFormat = new Intl.ListFormat("en-US", { type: "conjunction" });

/** Lists table counts with English conjunctions and each table name in bold. */
function tableList(tables: SavedTable[]) {
  let tableIndex = 0;
  return listFormat.formatToParts(tables.map((table) => table.name)).map((part, index) => {
    if (part.type === "literal") return part.value;
    const table = tables[tableIndex++];
    return (
      <Fragment key={index}>
        <strong>{table.name}</strong> ({table.rowCount.toLocaleString("en-US")} rows)
      </Fragment>
    );
  });
}

/** Shown after a save: which tables are in the local database, and a way into the data. */
export function UploadSavedCallout({ tables, joinKey, exploreHref, children }: UploadSavedCalloutProps) {
  const count = tables.length;
  return (
    <Alert role="status" className="flex flex-col gap-3 p-4">
      <AlertTitle>
        <h2 className="text-lg font-medium">Saved</h2>
      </AlertTitle>
      <AlertDescription className="flex flex-col gap-2">
        <p>
          {count} {count === 1 ? "table is" : "tables are"} in the local database: {tableList(tables)}
          {joinKey ? `, linked on ${joinKey}.` : "."}
        </p>
        {children}
      </AlertDescription>
      <div>
        <Link href={exploreHref} className={buttonVariants({ size: "lg" })}>
          Explore the data
        </Link>
      </div>
    </Alert>
  );
}
