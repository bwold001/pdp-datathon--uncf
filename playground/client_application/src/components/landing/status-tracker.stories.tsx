import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { expect } from 'storybook/test';

import type { HealthCheckRecord } from '@/lib/system-status';
import type { HealthResponse } from '@/services/health';

import { StatusTracker } from './status-tracker';

const health: HealthResponse = {
  status: 'ok',
  environment: 'development',
  version: '0.1.0',
  database: { engine: 'postgresql', status: 'connected', latency_ms: 3 },
};

const healthy = (id: number): HealthCheckRecord => ({
  id,
  checkedAt: Date.UTC(2026, 9, 30, 12, 0, id * 5),
  outcome: { reachable: true, health },
  roundTripMs: 12,
});

const meta = {
  component: StatusTracker, title: 'Components/Landing/Status tracker',
  args: { totalSlots: 30 },
} satisfies Meta<typeof StatusTracker>;

export default meta;
type Story = StoryObj<typeof meta>;

// Written out in full, not with the helpers above, so the components manifest can show it as an example.
export const FillingIn: Story = { name: 'Filling in',
  args: {
    history: [
      {
        id: 0,
        checkedAt: 1793361600000,
        roundTripMs: 12,
        outcome: {
          reachable: true,
          health: {
            status: 'ok',
            environment: 'development',
            version: '0.1.0',
            database: { engine: 'postgresql', status: 'connected', latency_ms: 3 },
          },
        },
      },
      {
        id: 1,
        checkedAt: 1793361605000,
        roundTripMs: 10004,
        outcome: { reachable: false, error: 'Could not reach the API at http://localhost:8000/api/v1' },
      },
    ],
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByRole('img')).toHaveAccessibleName('Last 2 health checks');
  },
};

export const Mixed: Story = {
  // Every state side by side, for people checking the shapes; FillingIn is the example for agents.
  tags: ['!manifest'],
  args: {
    history: [
      ...Array.from({ length: 20 }, (_, index) => healthy(index)),
      { ...healthy(20), outcome: { reachable: true, health: { ...health, status: 'degraded', database: { ...health.database, status: 'disconnected', latency_ms: null } } } },
      ...Array.from({ length: 5 }, (_, index) => ({
        ...healthy(21 + index),
        outcome: { reachable: false as const, error: 'Could not reach the API' },
      })),
      ...Array.from({ length: 4 }, (_, index) => healthy(26 + index)),
    ],
  },
};

export const Empty: Story = { name: 'No health checks yet', args: { history: [] } };
