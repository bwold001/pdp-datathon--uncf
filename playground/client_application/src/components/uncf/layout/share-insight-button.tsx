"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";

import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

import { explorerTabs } from "./explorer-config";
import { explorerButton } from "./explorer-styles";

/** The tallest page most PDF readers open: 200 inches, in points. */
const maxPdfPagePt = 200 * 72;
const ptPerPx = 72 / 96;

/**
 * Share Insight: the tab exactly as it looks on screen, as one long PDF page with no page breaks. It's drawn in the
 * browser, not printed, because print re-flows the page to the paper and splits it. Chat has no button: its messages
 * scroll inside a box that a picture would cut off.
 */
export function ShareInsightButton() {
  const pathname = usePathname();
  const [preparing, setPreparing] = useState(false);
  const tab = explorerTabs.find((each) => pathname.startsWith(each.href));
  if (!tab || tab.href === routes.uncfChat) return null;

  async function share(event: React.MouseEvent<HTMLButtonElement>) {
    const page = event.currentTarget.closest<HTMLElement>("[data-pdf-page]");
    if (!page || !tab) return;
    setPreparing(true);
    try {
      await downloadPageAsPdf(page, tab.label);
    } catch (error) {
      console.error("Couldn't make the page's PDF.", error);
    } finally {
      setPreparing(false);
    }
  }

  return (
    <button
      type="button"
      data-pdf-skip
      className={cn(explorerButton, "disabled:cursor-wait disabled:opacity-60")}
      onClick={share}
      disabled={preparing}
    >
      <DownloadIcon />
      {preparing ? "Preparing…" : "Share Insight"}
    </button>
  );
}

/** Draws the page to an image and downloads it as a single PDF page the page's size, scaled down only past the limit. */
async function downloadPageAsPdf(page: HTMLElement, name: string) {
  // Loaded on click, so they don't weigh on every tab.
  const [{ toPng }, { jsPDF }] = await Promise.all([import("html-to-image"), import("jspdf")]);
  const image = await toPng(page, {
    pixelRatio: 2,
    filter: (node) => !(node instanceof HTMLElement && node.dataset.pdfSkip !== undefined),
  });

  const scale = Math.min(1, maxPdfPagePt / (page.offsetHeight * ptPerPx));
  const width = page.offsetWidth * ptPerPx * scale;
  const height = page.offsetHeight * ptPerPx * scale;
  const pdf = new jsPDF({ unit: "pt", format: [width, height], orientation: width > height ? "landscape" : "portrait", compress: true });
  pdf.addImage(image, "PNG", 0, 0, width, height, undefined, "FAST");
  pdf.save(`${name}.pdf`);
}

/** The design's download arrow. */
function DownloadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden>
      <path
        d="M8 2v8M4.5 6.5 8 10l3.5-3.5M2.5 13.5h11"
        stroke="currentColor"
        strokeWidth="1.6"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
