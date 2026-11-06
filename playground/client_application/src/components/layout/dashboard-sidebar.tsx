import { SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupLabel, SidebarHeader } from "@/components/ui/sidebar";

type DashboardSidebarProps = {
  /** Header text. Omit for a sidebar without a header. */
  title?: string;
  /** Replaces `title` when the left sidebar collapses to icons. */
  shortTitle?: string;
  /** Label above the content group. */
  label?: string;
  /** Pinned below the scrolling content. */
  footer?: React.ReactNode;
  children: React.ReactNode;
};

/** Shared header, content group and footer for both `DashboardShell` sidebars. */
export function DashboardSidebar({ title, shortTitle, label, footer, children }: DashboardSidebarProps) {
  return (
    <>
      {title && (
        <SidebarHeader>
          <span className="truncate px-2 text-sm font-semibold group-data-[collapsible=icon]:hidden">{title}</span>
          {shortTitle && <span aria-hidden="true" className="hidden px-2 text-sm font-semibold group-data-[collapsible=icon]:block">{shortTitle}</span>}
        </SidebarHeader>
      )}
      {/* Focusable so keyboard users can scroll content that has no links or buttons, such as read-only panels. */}
      <SidebarContent tabIndex={0}>
        <SidebarGroup>
          {label && <SidebarGroupLabel>{label}</SidebarGroupLabel>}
          {children}
        </SidebarGroup>
      </SidebarContent>
      {footer && <SidebarFooter>{footer}</SidebarFooter>}
    </>
  );
}
