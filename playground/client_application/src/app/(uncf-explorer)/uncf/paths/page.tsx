import type { Metadata } from "next";

export const metadata: Metadata = { title: "Student paths" };

/** The Student paths tab. Its content comes in its own pull request. */
export default function StudentPathsPage() {
  return <h2 className="text-[28px] font-bold tracking-[-0.015em] md:text-[34px]">Student Paths</h2>;
}
