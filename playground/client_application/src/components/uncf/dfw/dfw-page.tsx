"use client";

import { useMemo, useState } from "react";

import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useApiResource } from "@/hooks/use-api-resource";

import { type DfwCourseDetail, type DfwList, type DfwSort, rankCourses } from "./dfw-data";
import { CourseDetail, CourseDetailError, CourseDetailLoading, CourseList, DfwCounted, DfwGradeCard, DfwKpis } from "./dfw-view";

const PAGE_SIZE = 10;

/** The DFW tab: loads the cohort bar's courses, then the selected course's groups. */
export function DfwPage() {
  const { apiQuery } = useCohortFilters();
  const loadList = useMemo(() => explorerLoader<DfwList>("/uncf/dfw", apiQuery), [apiQuery]);
  const { resource: list, retry: retryList } = useApiResource(loadList);
  useShowStudentCount(list.status !== "success" ? null : list.data.status === "suppressed" ? "under 10" : list.data.everyone.students);

  const [sort, setSort] = useState<DfwSort>("count");
  const [minimum, setMinimum] = useState(30);
  const [shown, setShown] = useState(PAGE_SIZE);
  const [chosen, setChosen] = useState<string | null>(null);
  const [dimension, setDimension] = useState("pell");

  const ranked = useMemo(() => (list.status === "success" ? rankCourses(list.data.courses, sort, minimum) : []), [list, sort, minimum]);
  // The chosen course while it's still in the list (a filter can drop it); otherwise the top one, as in the design.
  const selected = chosen && ranked.some((course) => course.course === chosen) ? chosen : (ranked[0]?.course ?? null);

  const loadDetail = useMemo(
    () => (selected ? explorerLoader<DfwCourseDetail>("/uncf/dfw/course", `${apiQuery}&course=${encodeURIComponent(selected)}`) : noDetail),
    [apiQuery, selected],
  );
  const { resource: detail, retry: retryDetail } = useApiResource(loadDetail);

  if (list.status === "loading") return <DfwLoading />;
  if (list.status === "error") {
    return (
      <MessageCard title="The DFW numbers couldn’t load." onRetry={retryList}>
        {list.message}
      </MessageCard>
    );
  }
  if (list.data.status === "suppressed") {
    return (
      <MessageCard title="Fewer than 10 students with final grades match these filters.">
        Remove a filter to see results. Groups under 10 students are hidden to protect privacy.
      </MessageCard>
    );
  }

  return (
    <>
      <DfwKpis everyone={list.data.everyone} />
      <DfwGradeCard everyone={list.data.everyone} />
      <div className="grid items-start gap-5 min-[961px]:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
        <CourseList
          courses={ranked.slice(0, shown)}
          total={ranked.length}
          sort={sort}
          minimum={minimum}
          selected={selected}
          onSelect={setChosen}
          onSort={(next) => {
            setSort(next);
            setShown(PAGE_SIZE);
          }}
          onMinimum={(next) => {
            setMinimum(next);
            setShown(PAGE_SIZE);
          }}
          onMore={shown < ranked.length ? () => setShown(shown + PAGE_SIZE) : undefined}
        />
        {selected === null ? (
          <MessageCard title="No course selected.">No courses match. Lower the size cutoff.</MessageCard>
        ) : detail.status === "error" ? (
          <CourseDetailError message={detail.message} onRetry={retryDetail} />
        ) : detail.status === "success" && detail.data?.course === selected ? (
          <CourseDetail detail={detail.data} dimension={dimension} onDimension={setDimension} />
        ) : (
          // Loading, or still showing the last course while the new one loads.
          <CourseDetailLoading />
        )}
      </div>
      <DfwCounted scale={list.data.meta.grade_scale} />
    </>
  );
}

/** No course to load. */
async function noDetail(): Promise<DfwCourseDetail | null> {
  return null;
}

/** Grey blocks in the shape of the tab while its numbers load. */
export function DfwLoading() {
  return (
    <div className="flex flex-col gap-7" aria-busy="true" aria-label="Loading DFW grades">
      <div className="grid gap-5 min-[961px]:grid-cols-3">
        {[0, 1, 2].map((n) => (
          <LoadingBlock key={n} className="h-38" />
        ))}
      </div>
      <div className="grid gap-5 min-[961px]:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
        <LoadingBlock className="h-140" />
        <LoadingBlock className="h-110" />
      </div>
    </div>
  );
}
