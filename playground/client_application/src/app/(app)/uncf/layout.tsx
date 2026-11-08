/** Every UNCF page: the page's width and padding, as the sandbox layout does. */
export default function UncfLayout({ children }: LayoutProps<"/uncf">) {
  return <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 pt-10 pb-24 sm:px-10 sm:pt-12">{children}</div>;
}
