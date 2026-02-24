/// <reference types="cypress" />

describe("Navigation & SEO Pages", () => {
  describe("Navigation", () => {
    it("has working logo link to homepage", () => {
      cy.visit("/");
      cy.get('a[href="/"]').first().click();
      cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
  });

  describe("Terms of Service", () => {
    beforeEach(() => {
      cy.visit("/terms");
    });

    it("loads successfully", () => {
      cy.get("main").should("be.visible");
    });

    it("contains legal disclaimers", () => {
      cy.contains(/not a law firm|not legal advice/i).should("exist");
    });

    it("contains limitation of liability", () => {
      cy.contains(/liability|limitation|responsible/i).should("exist");
    });
  });

  describe("Privacy Policy", () => {
    beforeEach(() => {
      cy.visit("/privacy");
    });

    it("loads successfully", () => {
      cy.get("main").should("be.visible");
    });
  });

  describe("What We Are Page", () => {
    beforeEach(() => {
      cy.visit("/what-we-are");
    });

    it("loads successfully", () => {
      cy.get("main").should("be.visible");
    });

    it("contains 'we're not lawyers' disclaimer", () => {
      cy.contains(/not lawyers|paperwork experts/i).should("be.visible");
    });

    it("explains what the service is", () => {
      cy.contains(/procedural compliance|document preparation/i).should("be.visible");
    });

    it("contains 'what we are not' section", () => {
      cy.contains(/what we are not|not a law firm/i).should("be.visible");
    });
  });

  describe("Blog", () => {
    beforeEach(() => {
      cy.visit("/blog");
    });

    it("loads successfully", () => {
      cy.get("main").should("be.visible");
    });

    it("displays blog posts", () => {
      cy.contains(/how to|guide|tips|appeal/i).should("be.visible");
    });
  });

  describe("City Pages", () => {
    it("loads SF city page", () => {
      cy.visit("/sf");
      cy.get("main").should("be.visible");
      cy.contains(/San Francisco/i).should("be.visible");
    });

    it("loads NYC city page", () => {
      cy.visit("/nyc");
      cy.get("main").should("be.visible");
      cy.contains(/New York/i).should("be.visible");
    });
  });

  describe("404 Page", () => {
    it("shows custom 404 for invalid routes", () => {
      cy.visit("/this-page-does-not-exist-12345");
      cy.contains(/not found|404/i).should("be.visible");
    });
  });
});
