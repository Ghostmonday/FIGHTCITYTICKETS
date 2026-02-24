/// <reference types="cypress" />

describe("Success Page", () => {
  beforeEach(() => {
    cy.visit("/success");
  });

  it("loads successfully after submission", () => {
    cy.get("main").should("be.visible");
  });

  it("shows confirmation message", () => {
    cy.contains(/success|confirmed|submitted|appeal/i).should("be.visible");
  });

  it("shows what's next steps", () => {
    cy.contains(/next|following|steps|what happens/i).should("be.visible");
  });

  it("shows estimated response time", () => {
    cy.contains(/weeks|months|response|decision/i).should("be.visible");
  });

  it("shows legal disclaimer", () => {
    cy.contains(/document preparation|not legal advice/i).should("be.visible");
  });

  it("has link back to homepage", () => {
    cy.get('a[href="/"]').should("exist");
  });
});

describe("Appeal Status Page", () => {
  it("loads the status page", () => {
    cy.visit("/appeal/status");
    cy.get("main").should("be.visible");
  });

  it("has status lookup form", () => {
    cy.visit("/appeal/status");
    cy.get('input[placeholder*="status" i]').should("exist");
    cy.get('input[placeholder*="email" i]').should("exist");
  });
});
