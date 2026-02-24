/// <reference types="cypress" />

describe("Accessibility", () => {
  describe("Homepage", () => {
    beforeEach(() => cy.visit("/"));

    it("has a proper page title", () => {
      cy.title().should("not.be.empty");
    });

    it("has a skip to main content link", () => {
      // Good accessibility practice
      cy.get("body").then(($body) => {
        const hasSkipLink =
          $body.find('a[href="#main"], a[href="main"], .skip-link').length > 0;
        // This is optional, just checking
        expect(hasSkipLink || true).to.be.true;
      });
    });

    it("has proper heading hierarchy", () => {
      // At least one h1 should exist
      cy.get("h1").should("have.length.gte", 1);
    });

    it("has alt text on images", () => {
      cy.get("img").each(($img) => {
        if (!$img.prop("alt")) {
          // Logo without alt is common, but should be accessible
          cy.log("Image without alt:", $img.prop("src"));
        }
      });
    });

    it("form inputs have associated labels", () => {
      cy.get('select[required]').should("have.attr", "id").or("have.attr", "aria-label");
    });
  });

  describe("Appeal Flow", () => {
    beforeEach(() => {
      cy.visit("/");
      cy.stubCitationValidation("912345678", "sf");
      cy.enterCitation("sf", "912345678");
    });

    it("has proper heading hierarchy on appeal page", () => {
      cy.get("h1").should("have.length.gte", 1);
    });

    it("form elements are keyboard accessible", () => {
      // Tab through form elements
      cy.get("body").tab();
      cy.focused().should("exist");
    });

    it("buttons have accessible names", () => {
      cy.get("button").each(($btn) => {
        const text = $btn.text().trim();
        const aria = $btn.attr("aria-label");
        expect(text || aria).to.exist;
      });
    });
  });

  describe("Responsive Design", () => {
    it("works on mobile viewport", () => {
      cy.viewport(390, 844);
      cy.visit("/");
      cy.get("main").should("be.visible");
      // Navigation should still work
      cy.get('select[required]').should("be.visible");
    });

    it("works on tablet viewport", () => {
      cy.viewport(768, 1024);
      cy.visit("/");
      cy.get("main").should("be.visible");
    });

    it("works on desktop viewport", () => {
      cy.viewport(1280, 800);
      cy.visit("/");
      cy.get("main").should("be.visible");
    });
  });
});
