import type { ComponentProps } from "react";
import { HomeDataLoaded } from "@/components/workbench/home/home-data-loaded";
import { TeamToolsSection } from "@/components/workbench/home/team-tools-section";

/** Synthetic example counts for stories, rather than findings about students. */
export const homeData: ComponentProps<typeof HomeDataLoaded> = {
  stats: [
    { id: "students", value: "10,313", label: "students" },
    { id: "cohorts", value: "4", label: "starting cohorts" },
    { id: "courses", value: "100,951", label: "course records" },
  ],
  lastUpload: { lastUpload: "today at 9:41 AM", warningCount: 23 },
  questions: {
    questions: [
      { question: "How many students receive Pell grants?", filterHint: "Pell = Yes", href: "#pell" },
      { question: "Who has completed gateway math?", filterHint: "Gateway math = Complete", href: "#math" },
    ],
  },
};

export const homeTools: ComponentProps<typeof TeamToolsSection> = {
  tools: [
    { id: "ask", name: "Ask about students", description: "Ask questions about the current group.", tag: "Example", href: "#ask" },
    { id: "add", name: "+ Add your tool", description: "Link your team's own feature here.", tag: "Your team", variant: "add", href: "#add" },
  ],
};
