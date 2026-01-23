/**
 * Appeal Context tests for FIGHTCITYTICKETS.com
 */

import { render, screen, act } from "@testing-library/react";
import { AppealProvider, useAppeal } from "./appeal-context";

// Test component that uses the context
function TestComponent() {
  const { state, updateState, clearState, getState } = useAppeal();

  return (
    <div>
      <span data-testid="citation">{state.citationNumber || "none"}</span>
      <span data-testid="city">{state.cityId || "none"}</span>
      <span data-testid="deadline">{state.appealDeadlineDays}</span>
      <button
        data-testid="update"
        onClick={() =>
          updateState({
            citationNumber: "912345678",
            cityId: "sf",
            appealDeadlineDays: 21,
          })
        }
      >
        Update
      </button>
      <button data-testid="clear" onClick={clearState}>
        Clear
      </button>
      <button data-testid="get" onClick={() => console.log(getState())}>
        Get State
      </button>
    </div>
  );
}

describe("Appeal Context", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe("Provider", () => {
    it("provides initial state to consumers", () => {
      render(
        <AppealProvider>
          <TestComponent />
        </AppealProvider>
      );

      expect(screen.getByTestId("citation")).toHaveTextContent("none");
      expect(screen.getByTestId("city")).toHaveTextContent("none");
      expect(screen.getByTestId("deadline")).toHaveTextContent("0");
    });

    it("allows updating state", () => {
      render(
        <AppealProvider>
          <TestComponent />
        </AppealProvider>
      );

      act(() => {
        screen.getByTestId("update").click();
      });

      expect(screen.getByTestId("citation")).toHaveTextContent("912345678");
      expect(screen.getByTestId("city")).toHaveTextContent("sf");
      expect(screen.getByTestId("deadline")).toHaveTextContent("21");
    });

    it("allows clearing state", () => {
      render(
        <AppealProvider>
          <TestComponent />
        </AppealProvider>
      );

      // First update
      act(() => {
        screen.getByTestId("update").click();
      });

      // Then clear
      act(() => {
        screen.getByTestId("clear").click();
      });

      expect(screen.getByTestId("citation")).toHaveTextContent("none");
      expect(screen.getByTestId("city")).toHaveTextContent("none");
      expect(screen.getByTestId("deadline")).toHaveTextContent("0");
    });
  });

  describe("State Persistence", () => {
    it("persists state to localStorage", () => {
      render(
        <AppealProvider>
          <TestComponent />
        </AppealProvider>
      );

      act(() => {
        screen.getByTestId("update").click();
      });

      // Check localStorage was called
      expect(localStorage.setItem).toHaveBeenCalledWith(
        "appeal_state",
        expect.any(String)
      );
    });

    it("loads state from localStorage on mount", () => {
      // Pre-populate localStorage
      const savedState = {
        citationNumber: "123456789",
        cityId: "la",
        sectionId: "ladot",
        appealDeadlineDays: 21,
        licensePlate: "ABC123",
        violationDate: "2024-01-15",
        signatureData: null,
      };
      localStorage.setItem("appeal_state", JSON.stringify(savedState));

      render(
        <AppealProvider>
          <TestComponent />
        </AppealProvider>
      );

      // The component should load the saved state
      expect(screen.getByTestId("citation")).toHaveTextContent("123456789");
      expect(screen.getByTestId("city")).toHaveTextContent("la");
    });
  });

  describe("useAppeal hook", () => {
    it("throws error when used outside provider", () => {
      // Suppress console.error for this test
      const consoleError = console.error;
      console.error = jest.fn();

      expect(() => {
        render(<TestComponent />);
      }).toThrow("useAppeal must be used within an AppealProvider");

      console.error = consoleError;
    });
  });
});
