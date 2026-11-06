import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { expect } from 'storybook/test';

import { BarList } from './bar-list';

const meta = {
  component: BarList, title: 'Components/Sandbox/Bar list',
} satisfies Meta<typeof BarList>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Percentages: Story = {
  name: 'Bars on a percentage scale',
  args: {
    items: [
      { label: 'All students', value: 61, display: '61%' },
      { label: 'Pell recipients', value: 48, display: '48%' },
      { label: 'First generation', value: 52, display: '52%' },
    ],
  },
};

/**
 * For values that aren't percents, set `max` to the longest bar's value, e.g. 8 terms.
 *
 * @summary for non-percent values; set max
 */
export const Terms: Story = {
  name: 'Term counts on a custom scale',
  args: {
    max: 8,
    items: [
      { label: 'Fall', value: 5.1, display: '5.1 terms' },
      { label: 'Spring', value: 5.8, display: '5.8 terms' },
      { label: 'Summer', value: 6.4, display: '6.4 terms' },
    ],
  },
};

/**
 * A value past `max` fills the track; its label still shows the real number.
 *
 * @summary values past max are capped, not hidden
 */
export const OverMax: Story = { name: 'Over max',
  args: {
    max: 8,
    items: [
      { label: 'Fall', value: 5.1, display: '5.1 terms' },
      { label: 'Part-time', value: 9.6, display: '9.6 terms' },
    ],
  },
  play: async ({ canvasElement }) => {
    const bars = canvasElement.querySelectorAll<HTMLElement>('[role="presentation"] > div');
    await expect(bars[1].style.width).toBe('100%');
  },
};
