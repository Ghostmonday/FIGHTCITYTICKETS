// Import Testing Library Cypress commands
import "@testing-library/cypress/add-commands";

// Import custom commands
import "./commands";

// Global before-each: clear sessionStorage between tests so appeal state is fresh
beforeEach(() => {
  cy.window().then((win) => win.sessionStorage.clear());
});

// Suppress known third-party errors that don't affect test validity
Cypress.on("uncaught:exception", (err) => {
  // Ignore Stripe.js / analytics errors in test env
  if (
    err.message.includes("stripe") ||
    err.message.includes("mixpanel") ||
    err.message.includes("ResizeObserver")
  ) {
    return false;
  }
});
