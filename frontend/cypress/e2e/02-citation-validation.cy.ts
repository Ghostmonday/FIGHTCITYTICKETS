/// <reference types="cypress" />

describe("Citation Validation Flow", () => {
  beforeEach(() => {
    cy.visit("/");
    // Stub the API for each test
    cy.stubCitationValidation("912345678", "sf");
  });

  it("successfully validates a citation and proceeds to appeal", () => {
    cy.enterCitation("sf", "912345678");

    // Should navigate to the appeal page
    cy.url().should("include", "/appeal");
    cy.wait("@validateCitation");
  });

  it("shows error for invalid citation format", () => {
    cy.enterCitation("sf", "abc");
    // The API might return an error or the frontend might validate format
    cy.get("body").should("contain", /invalid|error|check/i");
  });

  it("passes the selected city and citation to the appeal page", () => {
    cy.stubCitationValidation("1234567890", "nyc");
    cy.enterCitation("nyc", "1234567890");

    cy.wait("@validateCitation").then((interception) => {
      expect(interception.request.body.citation_number).to.eq("1234567890");
      expect(interception.request.body.city_id).to.eq("nyc");
    });
  });

  it("shows deadline information after validation", () => {
    cy.enterCitation("sf", "912345678");

    cy.url().should("include", "/appeal");
    // Check that appeal deadline info is displayed (21 days for SF)
    cy.contains(/21\s*days|days?\s*remaining/i).should("be.visible");
  });

  it("shows urgency warning for citations close to deadline", () => {
    cy.stubCitationValidation("912345678", "sf", {
      days_remaining: 3,
      is_urgent: true,
    });

    cy.enterCitation("sf", "912345678");

    cy.contains(/urgent|soon|limited/i).should("be.visible");
  });

  it("handles API errors gracefully", () => {
    cy.intercept("POST", "**/citation/validate", {
      statusCode: 500,
      body: { error: "Server error" },
    }).as("validateFail");

    cy.enterCitation("sf", "912345678");
    cy.contains(/error|try again|unavailable/i).should("be.visible");
  });
});
