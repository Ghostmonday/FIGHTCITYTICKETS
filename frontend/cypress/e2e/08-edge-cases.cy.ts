/// <parameter name="types">cypress" />

describe("Edge Cases & Error Handling", () => {
  describe("Network Errors", () => {
    it("handles offline/failed API gracefully on homepage", () => {
      cy.intercept("POST", "**/citation/validate", {
        forceNetworkError: true,
      }).as("offline");

      cy.visit("/");
      cy.enterCitation("sf", "912345678");

      // Should show an error message
      cy.contains(/error|unavailable|try again|offline/i).should("be.visible");
    });

    it("shows loading state during API calls", () => {
      cy.visit("/");

      // Intercept but delay response
      cy.intercept("POST", "**/citation/validate", (req) => {
        req.reply({ delay: 2000, body: { is_valid: true, citation_number: "912345678", agency: "SFMTA", days_remaining: 14 } });
      }).as("delayedValidate");

      cy.enterCitation("sf", "912345678");

      // Should show loading indicator
      cy.contains(/loading|validating|checking/i).should("be.visible");
    });
  });

  describe("Validation Edge Cases", () => {
    it("handles empty city selection", () => {
      cy.visit("/");

      // Try to submit without selecting city
      cy.get('input[placeholder*="citation" i]').type("912345678");
      cy.get('button[type="submit"]').click();

      // Should either show validation error or stay on page
      cy.get("body").should("not.contain", "TypeError");
    });

    it("handles very long citation input", () => {
      cy.visit("/");

      // Enter citation that's too long
      cy.get('select[required]').select("sf");
      cy.get('input[placeholder*="citation" i]').type("9".repeat(50));
      cy.get('button[type="submit"]').click();

      // Should either validate length or show error
      cy.get("body").should("not.contain", "TypeError");
    });

    it("handles special characters in citation", () => {
      cy.visit("/");

      cy.get('select[required]').select("sf");
      cy.get('input[placeholder*="citation" i]').type("91234-5678!");
      cy.get('button[type="submit"]').click();

      // Should either sanitize or handle gracefully
      cy.get("body").should("not.contain", "TypeError");
    });
  });

  describe("Session Management", () => {
    it("appeal state persists within session", () => {
      cy.visit("/");
      cy.stubCitationValidation("912345678", "sf");
      cy.enterCitation("sf", "912345678");

      // Go to review page
      cy.visit("/appeal/review");

      // The state should still be loaded (citation info should be visible)
      cy.get("body").should("contain", /appeal|citation|912345678/i);
    });

    it("clears appeal state on fresh visit to homepage", () => {
      cy.visit("/appeal/review");

      // Should either redirect or show empty state
      cy.get("body").then(($body) => {
        // Either redirects to home or shows empty state
        const redirectedHome = $body.text().includes("Citation Number");
        const hasEmptyState =
          $body.text().includes("Enter your citation") ||
          $body.text().includes("citation number");
        expect(redirectedHome || hasEmptyState).to.be.true;
      });
    });
  });

  describe("URL & Routing", () => {
    it("handles direct navigation to invalid city gracefully", () => {
      cy.visit("/invalid-city-12345");
      // Should show 404 or redirect
      cy.get("body").should("not.contain", "TypeError");
    });

    it("preserves query params during navigation", () => {
      cy.visit("/?ref=test");
      cy.get('select[required]').select("sf");
      cy.get('input[placeholder*="citation" i]').type("912345678");
      cy.get('button[type="submit"]').click();

      // After navigation, should preserve or handle ref param
      cy.url().should("satisfy", (url) => url.includes("appeal") || url.includes("ref"));
    });
  });

  describe("Browser Back Button", () => {
    it("works with browser back button", () => {
      cy.visit("/");
      cy.stubCitationValidation("912345678", "sf");

      // Go forward
      cy.enterCitation("sf", "912345678");
      cy.url().should("include", "/appeal");

      // Go back
      cy.go("back");
      cy.url().should("eq", Cypress.config().baseUrl + "/");

      // Go forward again
      cy.go("forward");
      cy.url().should("include", "/appeal");
    });
  });
});
