/// <reference types="cypress" />

describe("Appeal Flow", () => {
  beforeEach(() => {
    cy.visit("/");
    cy.stubCitationValidation("912345678", "sf");
    cy.enterCitation("sf", "912345678");
    cy.url().should("include", "/appeal");
    cy.stubStatementRefine();
  });

  describe("Appeal Page (/appeal)", () => {
    it("loads the appeal page with citation details", () => {
      cy.contains(/citation|912345678/i).should("be.visible");
    });

    it("has the photo upload section", () => {
      cy.contains(/photo|camera|upload/i).should("be.visible");
    });

    it("can navigate to the camera page", () => {
      cy.get('a[href*="camera"]').click();
      cy.url().should("include", "/appeal/camera");
    });
  });

  describe("Camera Page (/appeal/camera)", () => {
    beforeEach(() => {
      cy.visit("/appeal/camera");
    });

    it("has a camera access prompt or upload option", () => {
      cy.get("main").should("be.visible");
      // Should have either camera button or file upload
      cy.get("body").should("match", /camera|upload|file|select/i);
    });

    it("can skip photo and continue to review", () => {
      // Try to find a skip or continue button
      cy.get("body").then(($body) => {
        if ($body.find('a[href*="review"]').length > 0) {
          cy.get('a[href*="review"]').click();
        } else if ($body.find('button').filter(':contains("Continue")').length > 0) {
          cy.contains("Continue").click();
        }
      });
      cy.url().should("include", "/appeal/review");
    });
  });

  describe("Review Page (/appeal/review)", () => {
    beforeEach(() => {
      cy.visit("/appeal/review");
    });

    it("displays the statement textarea", () => {
      cy.get("textarea").should("exist");
    });

    it("shows AI refine button", () => {
      cy.contains(/refine|ai|improve/i).should("be.visible");
    });

    it("can edit the statement", () => {
      const newText = "My custom appeal reason.";
      cy.get("textarea").clear().type(newText);
      cy.get("textarea").should("have.value", newText);
    });

    it("can trigger AI refinement", () => {
      cy.get("textarea").clear().type("My ticket was wrong.");
      cy.contains(/refine/i).click();
      cy.wait("@refineStatement");
      // After refinement, textarea should have new content
      cy.get("textarea").invoke("val").should("have.length.gt", 10);
    });

    it("has legal disclaimer", () => {
      cy.contains(/not legal advice|document preparation/i).should("be.visible");
    });

    it("can proceed to signature", () => {
      cy.contains(/continue|next/i).click();
      cy.url().should("include", "/appeal/signature");
    });
  });

  describe("Signature Page (/appeal/signature)", () => {
    beforeEach(() => {
      cy.visit("/appeal/signature");
    });

    it("has name input field", () => {
      cy.get('input[type="text"]').first().should("exist");
    });

    it("has email input field", () => {
      cy.get('input[type="email"]').should("exist");
    });

    it("can enter signature information", () => {
      cy.get('input[type="text"]').first().type("John Doe");
      cy.get('input[type="email"]').type("john@example.com");
      cy.get('input[type="tel"]').type("555-123-4567");
    });

    it("has legal disclaimer", () => {
      cy.contains(/not legal advice/i).should("be.visible");
    });

    it("can proceed to pricing", () => {
      cy.get('input[type="text"]').first().type("John Doe");
      cy.get('input[type="email"]').type("john@example.com");
      cy.contains(/continue|next/i).click();
      cy.url().should("include", "/appeal/pricing");
    });
  });
});
