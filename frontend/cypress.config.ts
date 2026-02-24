import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:3000",
    specPattern: "cypress/e2e/**/*.cy.{ts,tsx}",
    supportFile: "cypress/support/e2e.ts",
    fixturesFolder: "cypress/fixtures",
    screenshotsFolder: "cypress/screenshots",
    videosFolder: "cypress/videos",
    video: false,
    screenshotOnRunFailure: true,

    viewportWidth: 1280,
    viewportHeight: 800,

    // Mobile viewport for responsive tests
    env: {
      mobileViewport: { width: 390, height: 844 },
      // Test citation numbers (format-valid but fake)
      sfCitation: "912345678",
      nycCitation: "1234567890",
      laCitation: "LA12345678901",
    },

    retries: {
      runMode: 2,
      openMode: 0,
    },

    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 30000,

    setupNodeEvents(on, config) {
      // Stub backend API calls in CI so tests don't need a running backend
      return config;
    },
  },
});
