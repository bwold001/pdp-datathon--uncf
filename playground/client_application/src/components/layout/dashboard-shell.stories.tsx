import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { BookOpenIcon, GraduationCapIcon, LayoutDashboardIcon, UsersIcon } from 'lucide-react';
import { expect, userEvent, within } from 'storybook/test';

import { SidebarNavMenu } from '@/components/layout/sidebar-nav-menu';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { SidebarGroupContent } from '@/components/ui/sidebar';

import { DashboardShell, useLeftSidebar, useRightSidebar } from './dashboard-shell';
import { Button } from '@/components/ui/button';
import { useSidebar } from '@/components/ui/sidebar';
import { DashboardSidebar } from './dashboard-sidebar';

const navItems = [
  { label: 'Overview', href: '#Overview', icon: LayoutDashboardIcon },
  { label: 'Enrollment', href: '#Enrollment', icon: UsersIcon },
  { label: 'Courses', href: '#Courses', icon: BookOpenIcon },
  { label: 'Completion', href: '#Completion', icon: GraduationCapIcon },
];

const leftSidebar = (
  <DashboardSidebar title="PDP Datathon" label="Dashboards">
    <SidebarNavMenu items={navItems} activeHref="#Overview" label="Dashboards" />
  </DashboardSidebar>
);

const rightSidebar = (
  <DashboardSidebar title="Filters" label="Cohort">
    <SidebarGroupContent className="px-2 text-muted-foreground">Fall 2020 through Fall 2023</SidebarGroupContent>
  </DashboardSidebar>
);

const meta = {
  component: DashboardShell,
  title: 'Components/Layout/Dashboard shell',
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: [
          'Full-page layout with independent navigation and context panels. Omit either sidebar slot to remove its panel and header toggle.',
          'The optional `shellTitle` prop is a plain-text label in the top bar and can accompany a page introduction; see **Without title** for a title-free top bar.',
          'Use `useLeftSidebar()` and `useRightSidebar()` from `dashboard-shell` for page controls; see **Page controls**. A bare `useSidebar()` in page content returns the right panel because its provider is nested inside the left provider.',
          '`contentProvider` wraps the page and right panel inside the right `SidebarProvider`, so a bare `useSidebar()` there also returns the right panel.',
        ].join('\n\n'),
      },
    },
  },
  args: {
    shellTitle: 'Overview',
    leftSidebar,
    rightSidebar,
    children: (
      <div className="grid gap-4 sm:grid-cols-3">
        {['Students', 'Retention', 'Credits earned'].map((title) => (
          <Card key={title}>
            <CardHeader>
              <CardTitle>{title}</CardTitle>
              <CardDescription>Synthetic data</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
    ),
  },
} satisfies Meta<typeof DashboardShell>;

export default meta;
type Story = StoryObj<typeof meta>;

const sidebar = (canvasElement: HTMLElement, side: 'left' | 'right') =>
  canvasElement.querySelector<HTMLElement>(`[data-slot="sidebar"][data-side="${side}"]`);

/**
 * Each toggle closes only its own sidebar.
 *
 * @summary left and right sidebars toggle independently
 */
export const Default: Story = {
  name: 'Default: Sidebars toggle independently',
  play: async ({ canvas, canvasElement }) => {
    const leftToggle = canvas.getByRole('button', { name: 'Toggle navigation' });
    const rightToggle = canvas.getByRole('button', { name: 'Toggle context panel' });
    await expect(leftToggle).toHaveAttribute('aria-expanded', 'true');
    await expect(rightToggle).toHaveAttribute('aria-expanded', 'true');

    await userEvent.click(leftToggle);
    await expect(leftToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(sidebar(canvasElement, 'left')).toHaveAttribute('data-state', 'collapsed');
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'expanded');

    await userEvent.click(rightToggle);
    await expect(rightToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'collapsed');
  },
};

/**
 * Ctrl/cmd+B collapses the navigation and leaves the context panel open.
 *
 * @summary the keyboard shortcut toggles only the left sidebar
 */
export const KeyboardShortcut: Story = {
  name: 'Keyboard shortcut',
  play: async ({ canvasElement }) => {
    await userEvent.keyboard('{Control>}b{/Control}');
    await expect(sidebar(canvasElement, 'left')).toHaveAttribute('data-state', 'collapsed');
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'expanded');
  },
};

/**
 * Below 768px each sidebar opens as a sheet over the page.
 *
 * @summary on phones the sidebars open as sheets
 */
export const Mobile: Story = {
  globals: { viewport: { value: 'mobile1', isRotated: false } },
  play: async ({ canvas, canvasElement }) => {
    await userEvent.click(canvas.getByRole('button', { name: 'Toggle navigation' }));
    const sheet = await within(canvasElement.ownerDocument.body).findByRole('dialog');
    // The navigation moved into the sheet. Not `toBeVisible`: the sheet fades in, so that depends on timing.
    await expect(within(sheet).getByText('Enrollment')).toBeInTheDocument();
  },
};

/** Omitting the navigation also omits its header control and the ctrl/cmd+B shortcut. */
export const WithoutNavigation: Story = {
  name: 'Without navigation',
  args: { leftSidebar: undefined },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.queryByRole('button', { name: 'Toggle navigation' })).not.toBeInTheDocument();
    await expect(sidebar(canvasElement, 'left')).toBeNull();
    await expect(canvas.getByRole('button', { name: 'Toggle context panel' })).toBeInTheDocument();

    // With no navigation, ctrl/cmd+B opens nothing and leaves the context panel as it was.
    await userEvent.keyboard('{Control>}b{/Control}');
    await expect(sidebar(canvasElement, 'left')).toBeNull();
    await expect(within(canvasElement.ownerDocument.body).queryByRole('dialog')).not.toBeInTheDocument();
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'expanded');
  },
};

/** Omitting the panel also omits its header control. */
export const WithoutContextPanel: Story = {
  name: 'Without context panel',
  args: { rightSidebar: undefined },
  play: async ({ canvas }) => {
    await expect(canvas.queryByRole('button', { name: 'Toggle context panel' })).not.toBeInTheDocument();
    await expect(canvas.getByRole('button', { name: 'Toggle navigation' })).toBeInTheDocument();
  },
};

/** Page controls select either sidebar even inside the nested right provider. */
function PageSidebarControls() {
  const left = useLeftSidebar();
  const right = useRightSidebar();
  const defaultSidebar = useSidebar();
  return (
    <>
      <Button onClick={left.toggleSidebar}>Toggle page navigation</Button>
      <Button onClick={right.toggleSidebar}>Toggle page details</Button>
      <p>Default panel: {defaultSidebar === right ? "right" : "left"}</p>
    </>
  );
}

/** Explicit hooks from page content toggle only their named panel. */
export const PageControls: Story = {
  name: 'Page controls target the correct sidebar',
  args: { children: <PageSidebarControls /> },
  play: async ({ canvas, canvasElement }) => {
    await expect(canvas.getByText('Default panel: right')).toBeInTheDocument();
    await userEvent.click(canvas.getByRole('button', { name: 'Toggle page navigation' }));
    await expect(sidebar(canvasElement, 'left')).toHaveAttribute('data-state', 'collapsed');
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'expanded');
    await userEvent.click(canvas.getByRole('button', { name: 'Toggle page details' }));
    await expect(sidebar(canvasElement, 'left')).toHaveAttribute('data-state', 'collapsed');
    await expect(sidebar(canvasElement, 'right')).toHaveAttribute('data-state', 'collapsed');
  },
};

/** The top bar can omit its label while keeping both sidebar controls. */
export const WithoutTitle: Story = {
  args: { shellTitle: undefined, children: <h1>Upload files</h1> },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole('heading', { level: 1, name: 'Upload files' })).toBeInTheDocument();
    await expect(canvas.getByRole('button', { name: 'Toggle navigation' })).toBeInTheDocument();
    await expect(canvas.getByRole('button', { name: 'Toggle context panel' })).toBeInTheDocument();
  },
};

/** Wide content scrolls inside the center pane while both sidebars stay in view. */
export const WideContent: Story = {
  name: 'Wide content, horizontal scroll',
  args: {
    children: (
      <div data-testid="wide-content" className="overflow-x-auto">
        <div className="min-w-[2000px]">Wide synthetic table content</div>
      </div>
    ),
  },
  play: async ({ canvas, canvasElement }) => {
    const content = canvas.getByTestId('wide-content');
    const inset = canvasElement.querySelector<HTMLElement>('[data-slot="sidebar-inset"]')!;
    await expect(content.scrollWidth).toBeGreaterThan(content.clientWidth);
    await expect(inset).toHaveClass('min-w-0');
    await expect(canvasElement.scrollWidth).toBeLessThanOrEqual(canvasElement.clientWidth);
    await expect(sidebar(canvasElement, 'right')).toBeVisible();
  },
};
