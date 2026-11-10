import type { Metadata } from "next";

export const metadata: Metadata = { title: "Gateway courses" };

/** The Gateway courses tab. Its content comes in its own pull request. */
export default function GatewayCoursesPage() {
  return <h2 className="text-[28px] font-bold tracking-[-0.015em] md:text-[34px]">Gateway Course Outcomes</h2>;
}
