import { redirect } from "next/navigation";

/** Preserve existing chat bookmarks in the Explorer. */
export default function LegacyChatPage() { redirect("/uncf/chat"); }
