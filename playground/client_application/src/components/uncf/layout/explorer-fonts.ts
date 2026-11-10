import { IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";

const plexSans = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-uncf-sans" });
const plexMono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-uncf-mono" });

/** Put on any element that should use the Explorer's type, with the uncf-type class. */
export const explorerFontClass = `uncf-type ${plexSans.variable} ${plexMono.variable}`;
