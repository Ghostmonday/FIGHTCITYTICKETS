
All imports now use @/lib/logger. Let me run a TypeScript check to verify everything compiles.DF/// <reference types="cypress" />

// ─── Custom Commands ─────────────────────────────────────────────────────────

/**
 * Stub the citation validation endpoint so tests work without a live backend.
 * Pass valid:false to simulate an invalid / unrecognized citation.
 */
Cypress.Commands.add(
  "stubCitationValidation",
  (
    citation: string,
    cityId: string,
    overrides: Partial<CypressCitationStub> = {}
  ) => {
    const defaults: CypressCitationStub = {
      is_valid: true,
      citation_number: citation,
      agency: "SFMTA",
      deadline_date: new Date(Date.now() + 14 * 86400000)
        .toISOString()
        .split("T")[0],
      days_remaining: 14,
      is_past_deadline: false,
      is_urgent: false,
      city_id: cityId,
      appeal_deadline_days: 21,
      clerical_defect_detected: false,
      clerical_defect_description: null,
    };

    cy.intercept("POST", "**/citation/validate", {
      statusCode: 200,
      body: { ...defaults, ...overrides },
    }).as("validateCitation");
  }
);

/**
 * Stub the statement refinement endpoint.
 */
Cypress.Commands.add("stubStatementRefine", (refinedText?: string) => {
  cy.intercept("POST", "**/statement/refine", {
    statusCode: 200,
    body: {
      status: "completed",
      original_statement: "test statement",
      refined_statement:
        refinedText ||
        "I am writing to formally appeal the above-referenced citation. The citation was issued in error as the meter was malfunctioning at the time of issuance.",
      method_used: "deepseek",
    },
  }).as("refineStatement");
});

/**
 * Stub Stripe checkout session creation.
 */
Cypress.Commands.add("stubStripeCheckout", () => {
  cy.intercept("POST", "**/payment/create-checkout-session", {
    statusCode: 200,
    body: { url: "https://checkout.stripe.com/test-session" },
  }).as("createCheckout");
});

/**
 * Walk through the citation entry step on the homepage.
 */
Cypress.Commands.add(
  "enterCitation",
  (cityValue: string, citation: string) => {
    cy.get('select[required]').select(cityValue);
    cy.get('input[placeholder*="citation" i], input[placeholder*="9123" i]')
      .first()
      .clear()
      .type(citation);
    cy.get('button[type="submit"]').click();
  }
);

/**
 * Wait for the appeal context to be ready (appeal page loaded).
 */
Cypress.Commands.add("waitForAppealPage", () => {
  cy.url().should("include", "/appeal");
  cy.get("main").should("be.visible");
});

// ─── Type declarations ────────────────────────────────────────────────────────

interface CypressCitationStub {
  is_valid: boolean;
  citation_number: string;
  agency: string;
  deadline_date: string;
  days_remaining: number;
  is_past_deadline: boolean;
  is_urgent: boolean;
  city_id: string;
  appeal_deadline_days: number;
  clerical_defect_detected: boolean;
  clerical_defect_description: string | null;
}

declare global {
  namespace Cypress {
    interface Chainable {
      stubCitationValidation(
        citation: string,
        cityId: string,
        overrides?: Partial<CypressCitationStub>
      ): Chainable<void>;
      stubStatementRefine(refinedText?: string): Chainable<void>;
      stubStripeCheckout(): Chainable<void>;
      enterCitation(cityValue: string, citation: string): Chainable<void>;
      waitForAppealPage(): Chainable<void>;
    }
  }
}
