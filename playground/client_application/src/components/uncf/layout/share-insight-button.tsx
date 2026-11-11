"use client";

import { Share } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { cn } from "@/lib/utils";

import { useStudentCount } from "./explorer-context";
import { explorerButton } from "./explorer-styles";
import { type ReportFacts, ShareInsightReport, describeView } from "./share-insight-report";

/** The tallest page most PDF readers open: 200 inches, in points. */
const maxPdfPagePt = 200 * 72;
const ptPerPx = 72 / 96;

/**
 * Share Insight, beside a tab's title: the tab as one long PDF page with no page breaks. The PDF is a report, not a
 * screenshot: who's counted in words instead of the cohort bar, then the tab without its controls (anything marked
 * data-pdf-skip). It's drawn in the browser, not printed, because print re-flows the page to the paper and splits it.
 */
export function ShareInsightButton({ name }: { name: string }) {
  const studentCount = useStudentCount();
  const [facts, setFacts] = useState<ReportFacts | null>(null);
  const tab = useRef<HTMLElement | null>(null);
  const report = useRef<HTMLDivElement>(null);
  const slot = useRef<HTMLDivElement>(null);

  function share(event: React.MouseEvent<HTMLButtonElement>) {
    tab.current = event.currentTarget.closest("main");
    if (!tab.current) return;
    setFacts(describeView(window.location.pathname, window.location.search, studentCount));
  }

  // Once the report is on the page, copy the tab into it, draw it, then take it away.
  useEffect(() => {
    if (!facts || !tab.current || !report.current || !slot.current) return;
    slot.current.replaceChildren(tab.current.cloneNode(true));
    downloadAsPdf(report.current, `${name} ${facts.cohort}`.trim())
      .catch((error) => console.error("Couldn't make the page's PDF.", error))
      .finally(() => setFacts(null));
  }, [facts, name]);

  return (
    <>
      <button
        type="button"
        data-pdf-skip
        className={cn(explorerButton, "shrink-0 self-start disabled:cursor-wait disabled:opacity-60")}
        onClick={share}
        disabled={facts !== null}
      >
        <Share className="size-4" aria-hidden />
        {facts ? "Preparing…" : "Share Insight"}
      </button>
      {facts &&
        createPortal(
          // Off screen, so the page doesn't change while the PDF is made.
          <div inert aria-hidden className="pointer-events-none fixed top-0 -left-[200vw]">
            <ShareInsightReport facts={facts} width={document.documentElement.clientWidth} ref={report} slotRef={slot} />
          </div>,
          document.body,
        )}
    </>
  );
}

/** Draws the report to an image and downloads it as a single PDF page its size, scaled down only past the limit. */
async function downloadAsPdf(page: HTMLElement, name: string) {
  // Loaded on click, so they don't weigh on every tab.
  const [{ toPng }, { jsPDF }] = await Promise.all([import("html-to-image"), import("jspdf")]);
  await document.fonts.ready;
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
