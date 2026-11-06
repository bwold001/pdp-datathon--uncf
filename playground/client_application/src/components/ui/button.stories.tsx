import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { ArrowRight, Moon, RotateCw } from 'lucide-react';
import Link from 'next/link';
import { expect, fn } from 'storybook/test';

import { routes } from '@/lib/routes';

import { Button, buttonVariants } from './button';

const meta = {
  component: Button, title: 'Components/UI/Button',
  args: { onClick: fn() },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: "Default Button State",
  args: { children: 'See example charts', size: 'lg' },
  play: async ({ args, canvas, userEvent }) => {
    await userEvent.click(canvas.getByRole('button', { name: /see example charts/i }));
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    size: 'sm',
    children: (
      <>
        <RotateCw aria-hidden /> Try again
      </>
    ),
  },
};

export const Ghost: Story = { args: { variant: 'ghost', children: 'Cancel' } };

export const Destructive: Story = { args: { variant: 'destructive', children: 'Delete' } };

export const Disabled: Story = {
  args: { children: 'Submit', disabled: true },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole('button', { name: /submit/i })).toBeDisabled();
  },
};

/**
 * An icon with no visible text, like the theme toggle. Give it an `aria-label` so screen readers can name it.
 *
 * @summary for icon-only controls; needs an aria-label
 */
export const IconOnly: Story = { name: 'Icon only',
  args: { variant: 'ghost', size: 'icon', 'aria-label': 'Toggle light and dark mode', children: <Moon /> },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole('button')).toHaveAccessibleName('Toggle light and dark mode');
  },
};

/**
 * When the click goes to another page, use a `next/link` styled with `buttonVariants`, not a `Button`.
 *
 * @summary for navigation that should look like a button
 */
export const AsLink: Story = { name: 'As link',
  render: () => (
    <Link href={routes.sandboxChartExamples} className={buttonVariants({ size: 'lg' })}>
      See example charts
      <ArrowRight aria-hidden />
    </Link>
  ),
  play: async ({ canvas }) => {
    await expect(canvas.getByRole('link', { name: /see example charts/i })).toHaveAttribute('href', routes.sandboxChartExamples);
  },
};

export const CssCheck: Story = { name: 'CSS check',
  // A test that Storybook loaded the app's CSS, not an example of how to use Button.
  tags: ['!manifest'],
  args: { children: 'Submit' },
  play: async ({ canvas }) => {
    const button = canvas.getByRole('button', { name: /submit/i });
    // Missing Tailwind leaves the button transparent; the theme's exact color can change.
    await expect(getComputedStyle(button).backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
    await expect(getComputedStyle(button).backgroundColor).not.toBe('transparent');
  },
};
