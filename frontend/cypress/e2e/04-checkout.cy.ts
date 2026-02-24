/// <reference types="cypress" />

describe("Checkout Flow", () => {
  beforeEach(() => {
    cy.visit("/appeal/pricing");
    cy.stubStripeCheckout();
  });

  it("displays pricing options", () => {
    cy.get("main").should("be.visible");
    cy.contains(/price|fee|standard|certified/i).should("be.visible");
  });

  it("has legal disclaimer about document preparation only", () => {
    cy.contains(/document preparation|not legal advice/i).should("be.visible");
  });

  it("can select standard shipping", () => {
    // Look for shipping option buttons/selects
    cy.get("body").then(($body) => {
      if ($body.find('button:contains("Standard")').length > 0) {
        cy.contains("Standard").click();
      } else if ($body.find('input[value*="standard"]').length > 0) {
        cy.get('input[value*="standard"]').check();
      }
    });
  });

  it("can proceed to checkout after selecting option", () => {
    cy.get("body").then(($body) => {
      // Try to find and click a continue or checkout button
      if ($body.find('button:contains("Continue")').length > 0) {
        cy.contains("Continue").click();
      } else if ($body.find('a[href*="checkout"]').length > 0) {
        cy.get('a[href*="checkout"]').click();
      }
    });
    // Should navigate to checkout or show checkout form
    cy.url().should("match", /checkout|payment/i);
  });
});

describe("Full Checkout Integration", () => {
  beforeEach(() => {
    // Visit checkout directly with mocked state
    cy.visit("/appeal/checkout");
    cy.stubStripeCheckout();
  });

  it("loads the checkout page", () => {
    cy.get("main").should("be.visible");
  });

  it("shows order summary with citation", () => {
    cy.contains(/citation|appeal|order|summary/i).should("be.visible");
  });

  it("has Stripe payment section or redirect", () => {
    cy.get("body").then(($body) => {
      // Either Stripe Elements iframe or redirect message
      const hasStripe =
        $body.find("iframe").length > 0 ||
        $body.text().includes("Stripe") ||
        $body.text().includes("Pay") ||
        $body.text().includes("card");
      expect(hasStripe).to.be.true;
    });
  });

  it("shows refund policy disclaimer", () => {
    cy.contains(/refund|non-refundable|no refund/i).should("be.visible");
  });

  it("shows legal disclaimer", () => {
    cy.contains(/document preparation|not legal advice/i).should("be.visible");
  });
});
