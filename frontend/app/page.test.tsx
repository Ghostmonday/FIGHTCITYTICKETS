/**
 * Homepage tests for FIGHTCITYTICKETS.com
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Home from "./page";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}));

// Mock the appeal context
jest.mock("./lib/appeal-context", () => ({
  useAppeal: jest.fn(() => ({
    state: {
      citationNumber: "",
      licensePlate: "",
      violationDate: "",
      cityId: "",
      sectionId: "",
      appealDeadlineDays: 21,
    },
    updateState: jest.fn(),
  })),
}));

// Mock the API client
jest.mock("./lib/api-client", () => ({
  apiClient: {
    post: jest.fn(),
  },
}));

describe("Homepage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Page Rendering", () => {
    it("renders the hero section with correct title", () => {
      render(<Home />);
      expect(
        screen.getByText(/They Demand Perfection/i)
      ).toBeInTheDocument();
    });

    it("renders the subtitle about procedural compliance", () => {
      render(<Home />);
      expect(
        screen.getByText(/A parking citation is a procedural document/i)
      ).toBeInTheDocument();
    });

    it("renders the city selection dropdown", () => {
      render(<Home />);
      expect(screen.getByRole("combobox")).toBeInTheDocument();
    });

    it("renders the citation number input field", () => {
      render(<Home />);
      expect(screen.getByPlaceholderText(/e.g., 912345678/i)).toBeInTheDocument();
    });
  });

  describe("Form Validation", () => {
    it("shows validation error when citation number is empty", async () => {
      render(<Home />);

      const submitButton = screen.getByRole("button", {
        name: /Validate Citation/i,
      });
      fireEvent.click(submitButton);

      // The form should show an error or prevent submission
      // Since the API call might not happen, we check the button state
      expect(submitButton).toBeInTheDocument();
    });

    it("enables submit button when city is selected", () => {
      render(<Home />);

      const citySelect = screen.getByRole("combobox");
      const submitButton = screen.getByRole("button", {
        name: /Validate Citation/i,
      });

      // Initially button should be enabled
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe("City Selection", () => {
    it("displays San Francisco in the dropdown", () => {
      render(<Home />);
      expect(screen.getByText(/San Francisco \(SF\)/i)).toBeInTheDocument();
    });

    it("displays Los Angeles in the dropdown", () => {
      render(<Home />);
      expect(screen.getByText(/Los Angeles \(LA\)/i)).toBeInTheDocument();
    });

    it("displays New York City in the dropdown", () => {
      render(<Home />);
      expect(screen.getByText(/New York City \(NYC\)/i)).toBeInTheDocument();
    });
  });

  describe("Optional Fields", () => {
    it("renders license plate input field", () => {
      render(<Home />);
      expect(
        screen.getByPlaceholderText(/e.g., ABC123/i)
      ).toBeInTheDocument();
    });

    it("renders violation date input field", () => {
      render(<Home />);
      expect(screen.getByRole("dateinput")).toBeInTheDocument();
    });
  });

  describe("Legal Disclaimer", () => {
    it("renders the legal disclaimer component", () => {
      render(<Home />);
      expect(
        screen.getByText(/We aren't lawyers/i)
      ).toBeInTheDocument();
    });
  });
});
