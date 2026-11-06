import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { expect, mocked } from 'storybook/test';

import { useHealthMonitor } from '@/hooks/use-health-monitor';
import type { HealthCheckRecord } from '@/lib/system-status';

import { LiveStatus } from './live-status';

// Synthetic snapshots keep the stories repeatable without an API or polling timer.
const connected: HealthCheckRecord = {
  id: 0,
  checkedAt: Date.UTC(2026, 9, 30, 12),
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
};

const databaseUnavailable: HealthCheckRecord = {
  ...connected,
  id: 1,
  checkedAt: connected.checkedAt + 5_000,
  outcome: {
    reachable: true,
    health: {
      status: 'degraded',
      environment: 'development',
      version: '0.1.0',
      database: { engine: 'postgresql', status: 'disconnected', latency_ms: null },
    },
  },
};

const serverUnavailable: HealthCheckRecord = {
  ...connected,
  id: 2,
  checkedAt: connected.checkedAt + 10_000,
  roundTripMs: 10_000,
  outcome: { reachable: false, error: 'Could not reach the API' },
};

const meta = {
  component: LiveStatus,
  title: 'Components/Landing/Live status',
  parameters: {
    docs: {
      description: {
        component: 'Mock a data-fetching hook with sb.mock in .storybook/preview.tsx, then use mocked(hook).mockReturnValue in each story’s beforeEach. These synthetic health snapshots never call the API.',
      },
    },
  },
} satisfies Meta<typeof LiveStatus>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Checking: Story = {
  name: 'Checking the connection',
  // Exercise the project default without a story-level hook override.
  play: async ({ canvas }) => {
    await expect(canvas.getByText('Checking connection…')).toBeInTheDocument();
    await expect(canvas.getByRole('img', { name: 'Last 0 health checks' })).toBeInTheDocument();
  },
};

export const Connected: Story = {
  name: 'API and database connected',
  beforeEach: () => {
    mocked(useHealthMonitor).mockReturnValue({ history: [connected], latest: connected });
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText('All systems connected')).toBeInTheDocument();
    await expect(canvas.getByText('API v0.1.0')).toBeInTheDocument();
    await expect(canvas.getByRole('img', { name: 'Last 1 health checks' })).toBeInTheDocument();
  },
};

/** The API is reachable but reports its database as disconnected. */
export const DatabaseUnavailable: Story = { name: 'Database unavailable',
  beforeEach: () => {
    mocked(useHealthMonitor).mockReturnValue({
      history: [connected, databaseUnavailable], latest: databaseUnavailable,
    });
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText('Server application up, database unreachable')).toBeInTheDocument();
    await expect(canvas.getByRole('img', { name: 'Last 2 health checks' })).toBeInTheDocument();
  },
};

export const ServerUnavailable: Story = { name: 'Server unavailable',
  beforeEach: () => {
    mocked(useHealthMonitor).mockReturnValue({
      history: [connected, databaseUnavailable, serverUnavailable], latest: serverUnavailable,
    });
  },
  play: async ({ canvas }) => {
    await expect(canvas.getByText('Server application unreachable')).toBeInTheDocument();
    await expect(canvas.getByRole('img', { name: 'Last 3 health checks' })).toBeInTheDocument();
  },
};
