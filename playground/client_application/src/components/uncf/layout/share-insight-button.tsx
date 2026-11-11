"use client";

import { Share } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/utils";

import { explorerButton } from "./explorer-styles";

/** The tallest page most PDF readers open: 200 inches, in points. */
const maxPdfPagePt = 200 * 72;
const ptPerPx = 72 / 96;

/**
 * Share Insight, beside a tab's title: the tab exactly as it looks on screen, as one long PDF page with no page breaks,
 * filters included. It's drawn in the browser, not printed, because print re-flows the page to the paper and splits it.
 */
export function ShareInsightButton({ name }: { name: string }) {
  const [preparing, setPreparing] = useState(false);

  async function share(event: React.MouseEvent<HTMLButtonElement>) {
    const page = event.currentTarget.closest<HTMLElement>("[data-pdf-page]");
    if (!page) return;
    setPreparing(true);
    try {
      await downloadPageAsPdf(page, name);
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
      className={cn(explorerButton, "shrink-0 self-start disabled:cursor-wait disabled:opacity-60")}
      onClick={share}
      disabled={preparing}
    >
      <Share className="size-4" aria-hidden />
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
