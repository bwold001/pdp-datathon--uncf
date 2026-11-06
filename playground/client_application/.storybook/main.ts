import type { StorybookConfig } from '@storybook/nextjs-vite';
import tailwindcss from '@tailwindcss/vite';

const config: StorybookConfig = {
  "stories": [
    "../src/**/*.mdx",
    "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"
  ],
  "addons": [
    "@storybook/addon-vitest",
    "@storybook/addon-a11y",
    "@storybook/addon-docs",
    "@storybook/addon-mcp"
  ],
  "framework": "@storybook/nextjs-vite",
  "staticDirs": [
    "../public"
  ],
  // Lets the MCP server's docs tools list components and their props (see .mcp.json at the repo root).
  "features": {
    "componentsManifest": true
  },
  // The app compiles Tailwind with @tailwindcss/turbopack; Storybook builds with Vite, so it needs the Vite plugin.
  async viteFinal(config) {
    config.plugins = [...(config.plugins ?? []), tailwindcss()];
    return config;
  }
};
export default config;
