import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

export default defineConfig([
  // Base Next.js + Core Web Vitals recommended rules
  ...nextVitals,
  
  // TypeScript rules
  ...nextTs,

  // Override specific rules
  {
    rules: {
      "@next/next/no-img-element": "off",
    },
  },

  // Global ignores
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "node_modules/**",
  ]),
]);
