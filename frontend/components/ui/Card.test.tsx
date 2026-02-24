import { render, screen } from "@testing-library/react";
import React, { createRef } from "react";
import { Card } from "./Card";

describe("Card", () => {
  it("renders children correctly", () => {
    render(<Card>Test Content</Card>);
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  describe("variants", () => {
    it("renders default variant correctly", () => {
      render(<Card variant="default">Default Card</Card>);
      const card = screen.getByText("Default Card");
      expect(card).toHaveClass("bg-bg-surface", "border", "border-border");
    });

    it("renders elevated variant correctly", () => {
      render(<Card variant="elevated">Elevated Card</Card>);
      const card = screen.getByText("Elevated Card");
      expect(card).toHaveClass("bg-bg-surface", "shadow-elevation");
    });

    it("renders outlined variant correctly", () => {
      render(<Card variant="outlined">Outlined Card</Card>);
      const card = screen.getByText("Outlined Card");
      expect(card).toHaveClass("bg-bg-surface", "border-2", "border-border");
    });
  });

  describe("padding", () => {
    it("renders none padding correctly", () => {
      render(<Card padding="none">None Padding</Card>);
      const card = screen.getByText("None Padding");
      expect(card).not.toHaveClass("p-4");
      expect(card).not.toHaveClass("p-6");
      expect(card).not.toHaveClass("p-8");
    });

    it("renders sm padding correctly", () => {
      render(<Card padding="sm">Small Padding</Card>);
      const card = screen.getByText("Small Padding");
      expect(card).toHaveClass("p-4");
    });

    it("renders md padding correctly", () => {
      render(<Card padding="md">Medium Padding</Card>);
      const card = screen.getByText("Medium Padding");
      expect(card).toHaveClass("p-6");
    });

    it("renders lg padding correctly", () => {
      render(<Card padding="lg">Large Padding</Card>);
      const card = screen.getByText("Large Padding");
      expect(card).toHaveClass("p-8");
    });
  });

  it("applies hover styles when hover prop is true", () => {
    render(<Card hover>Hover Card</Card>);
    const card = screen.getByText("Hover Card");
    expect(card).toHaveClass(
      "hover:shadow-elevation",
      "hover:border-border-subtle",
      "transition-all",
      "duration-200",
      "cursor-pointer"
    );
  });

  it("forwards ref to the underlying div", () => {
    const ref = createRef<HTMLDivElement>();
    render(<Card ref={ref}>Ref Card</Card>);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
    expect(ref.current).toHaveTextContent("Ref Card");
  });

  it("merges custom className with default styles", () => {
    render(<Card className="custom-class">Custom Class Card</Card>);
    const card = screen.getByText("Custom Class Card");
    expect(card).toHaveClass("custom-class");
    expect(card).toHaveClass("rounded-card"); // Default style
  });

  it("passes additional props to the underlying div", () => {
    render(<Card data-testid="test-card" id="card-id">Props Card</Card>);
    const card = screen.getByTestId("test-card");
    expect(card).toHaveAttribute("id", "card-id");
  });
});
