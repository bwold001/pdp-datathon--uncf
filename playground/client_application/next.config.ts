import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  /** Resolve old chat bookmarks before the disabled production Sandbox layout runs. */
  redirects() {
    return [{ source: "/sandbox/data-chat-ui", destination: "/uncf/chat", permanent: false }];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
