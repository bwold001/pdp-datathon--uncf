"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { SidebarMenu, SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";

export type SidebarNavMenuItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  note?: string;
};

/** Navigation content only. Its caller supplies selection and any navigation side effect. */
export function SidebarNavMenu({ items, activeHref, label = "Main navigation", onNavigate }: {
  items: SidebarNavMenuItem[];
  activeHref?: string;
  label?: string;
  onNavigate?: () => void;
}) {
  return (
    <nav aria-label={label}>
      <SidebarMenu>
        {items.map((item) => (
          <SidebarMenuItem key={item.href}>
            <SidebarMenuButton
              isActive={item.href === activeHref}
              tooltip={item.label}
              className={cn(item.note && "pr-16")}
              // Capture before Link/Tooltip's composed bubble handlers prevent the native click.
              onClickCapture={(event) => {
                if (!event.defaultPrevented && event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) onNavigate?.();
              }}
              render={<Link href={item.href} aria-current={item.href === activeHref ? "page" : undefined} />}
            >
              <item.icon aria-hidden="true" />
              <span>{item.label}</span>
            </SidebarMenuButton>
            {item.note && <SidebarMenuBadge>{item.note}</SidebarMenuBadge>}
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </nav>
  );
}
