// Class lists the Explorer repeats. Tabs can use them too, so their content lines up with the header.

/** The page's width and side gutters, shared by the header, the tabs, the cohort bar and each tab's content. */
export const explorerWrap = "mx-auto w-full max-w-[1240px] px-4 sm:px-6 lg:px-8";

/** The outlined button from the design. */
export const explorerButton =
  "inline-flex cursor-pointer items-center gap-2 rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-4 py-2 font-medium whitespace-nowrap hover:border-(--uncf-ink-3)";

/** The filled blue button, for the one main action in a group. */
export const explorerPrimaryButton =
  "inline-flex cursor-pointer items-center gap-2 rounded-md border border-(--uncf-blue) bg-(--uncf-blue) px-4 py-2 font-medium whitespace-nowrap text-white";

/** A plain underlined text button, like Reset and Clear. */
export const explorerLinkButton = "cursor-pointer text-(--uncf-ink-2) underline hover:text-(--uncf-ink)";
