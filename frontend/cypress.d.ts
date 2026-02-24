/// <reference types="cypress" />

// Custom commands added in cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      stubCitationValidation(
        citation: string,
        cityId: string,
        overrides?: Record<string, unknown>
      ): Chainable<void>;
      stubStatementRefine(refinedText?: string): Chainable<void>;
      stubStripeCheckout(): Chainable<void>;
      enterCitation(cityValue: string, citation: string): Chainable<void>;
      waitForAppealPage(): Chainable<void>;
    }
  }
}

export {};
