/// <reference types="cypress" />

describe("Homepage", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("loads without crashing", () => {
    cy.get("main").should("be.visible");
  });

  it("displays the hero section with headline", () => {
    cy.contains("They Demand Perfection").should("be.visible");
  });

  it("shows the legal disclaimer", () => {
    cy.contains(/we aren't lawyers|we're paperwork experts/i).should("be.visible");
  });

  it("has the city selector dropdown", () => {
    cy.get('select[required]').should("exist");
    cy.get('select[required] option').should("have.length.gt", 1);
  });

  it("has a citation input field", () => {
    cy.get('input[type="text"]')
      .first()
      .should("have.attr", "placeholder")
      .and("include", "citation");
  });

  it("can select a city from the dropdown", () => {
    cy.get('select[required]').select("sf");
    cy.get('select[required]').should("have.value", "sf");
  });

  it("validates required fields before submission", () => {
    cy.get('button[type="submit"]').click();
    // Should show validation error or stay on page
    cy.url().should("eq", Cypress.config().baseUrl + "/");
  });
});
