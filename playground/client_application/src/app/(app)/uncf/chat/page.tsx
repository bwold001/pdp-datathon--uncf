import { redirect } from "next/navigation";

/** Preserve existing chat bookmarks after the ownership cleanup. */
export default function LegacyChatPage() { redirect("/chat"); }
