import type { Preview } from '@storybook/nextjs-vite'
import { Inter } from 'next/font/google'
import { mocked, sb } from 'storybook/test'

import '../src/app/globals.css'
import { ThemeProvider } from '../src/components/theme-provider'
import { useHealthMonitor } from '../src/hooks/use-health-monitor'

// Replace polling in Storybook; stories can override the default empty history below.
sb.mock('../src/hooks/use-health-monitor.ts')

// Mirrors src/app/layout.tsx, which Storybook doesn't render: globals.css reads --font-sans from this class.
const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })
document.documentElement.classList.add('font-sans', 'antialiased', inter.variable)

const preview: Preview = {
  // A Docs page for every component: its description, props table and stories, built from the source.
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
    // Keeps sidebars (fixed to the viewport) inside their docs example, so stories can render inline:
    // inline examples don't autoplay play functions by default and load faster than one iframe per story.
    (Story, { viewMode }) => {
      if (viewMode !== 'docs') return <Story />;
      return (
        // The transform makes this box, not the viewport, the containing block for position: fixed.
        // Only examples with a sidebar get it, plus a 480px minimum; the box grows with the page content.
        <div
          className={[
            'has-[[data-slot=sidebar-wrapper]]:transform-gpu',
            'has-[[data-slot=sidebar-wrapper]]:min-h-[480px] has-[[data-slot=sidebar-wrapper]]:overflow-hidden',
            '[&_[data-slot=sidebar-wrapper]]:min-h-[480px] [&_[data-slot=sidebar-container]]:h-full',
          ].join(' ')}
        >
          <Story />
        </div>
      );
    },
  ],
  beforeEach() {
    // next-themes reads this key; light keeps colors the same on every machine.
    localStorage.setItem('theme', 'light');
    // Keep LiveStatus safe to render even when a story does not configure the hook.
    mocked(useHealthMonitor).mockReturnValue({ history: [], latest: undefined });
  },
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo'
    }
  },
};

export default preview;
