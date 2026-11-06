"use client";

import type { ComponentProps } from "react";
import { HomeDataLoaded } from "@/components/workbench/home/home-data-loaded";
import { HomeFirstRun } from "@/components/workbench/home/home-first-run";
import { TeamToolsSection } from "@/components/workbench/home/team-tools-section";

export type HomePageProps = { tools: ComponentProps<typeof TeamToolsSection> } & (
  | { hasData: false; firstRun: ComponentProps<typeof HomeFirstRun>; dataLoaded?: never }
  | { hasData: true; dataLoaded: ComponentProps<typeof HomeDataLoaded>; firstRun?: never }
);

/** Chooses the Home view and shows team tools whenever any are registered. */
export function HomePage(props: HomePageProps) {
  return (
    <div className="flex flex-col gap-6">
      {props.hasData ? (
        <HomeDataLoaded {...props.dataLoaded} />
      ) : (
        <HomeFirstRun {...props.firstRun} />
      )}
      {props.tools.tools.length > 0 && <TeamToolsSection {...props.tools} />}
    </div>
  );
}
