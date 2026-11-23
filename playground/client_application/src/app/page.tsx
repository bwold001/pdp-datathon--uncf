import { redirect } from "next/navigation";

import { routes } from "@/lib/routes";

/** The app's home is the Explorer's first tab, as on the deployed site (vercel.json). */
export default function HomePage() {
  redirect(routes.uncfPaths);
}
