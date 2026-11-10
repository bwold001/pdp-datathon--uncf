import type { Metadata } from "next";

export const metadata: Metadata = { title: "DFW" };

/** The DFW tab. Its content comes in its own pull request. */
export default function DfwPage() {
  return <h2 className="text-[28px] font-bold tracking-[-0.015em] md:text-[34px]">DFW</h2>;
}
