import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./Button";
import { createRef } from "react";

describe("Button", () => {
  it("renders with default props", () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole("button", { name: /click me/i });
    expect(button).toBeInTheDocument();
    // Default primary variant checks
    expect(button).toHaveClass("bg-primary");
    expect(button).toHaveClass("text-white");
    // Default md size checks
    expect(button).toHaveClass("px-6");
    expect(button).toHaveClass("py-3");
    expect(button).not.toBeDisabled();
  });

  describe("Variants", () => {
    it("renders primary variant", () => {
      render(<Button variant="primary">Primary</Button>);
      const button = screen.getByRole("button", { name: /primary/i });
      expect(button).toHaveClass("bg-primary");
      expect(button).toHaveClass("text-white");
    });

    it("renders secondary variant", () => {
      render(<Button variant="secondary">Secondary</Button>);
      const button = screen.getByRole("button", { name: /secondary/i });
      expect(button).toHaveClass("bg-bg-surface");
      expect(button).toHaveClass("text-text-primary");
      expect(button).toHaveClass("border");
      expect(button).toHaveClass("border-border");
    });

    it("renders ghost variant", () => {
      render(<Button variant="ghost">Ghost</Button>);
      const button = screen.getByRole("button", { name: /ghost/i });
      expect(button).toHaveClass("bg-transparent");
      expect(button).toHaveClass("text-text-secondary");
    });
  });

  describe("Sizes", () => {
    it("renders sm size", () => {
      render(<Button size="sm">Small</Button>);
      const button = screen.getByRole("button", { name: /small/i });
      expect(button).toHaveClass("px-4");
      expect(button).toHaveClass("py-2");
      expect(button).toHaveClass("text-sm");
    });

    it("renders md size", () => {
      render(<Button size="md">Medium</Button>);
      const button = screen.getByRole("button", { name: /medium/i });
      expect(button).toHaveClass("px-6");
      expect(button).toHaveClass("py-3");
      expect(button).toHaveClass("text-body");
    });

    it("renders lg size", () => {
      render(<Button size="lg">Large</Button>);
      const button = screen.getByRole("button", { name: /large/i });
      expect(button).toHaveClass("px-8");
      expect(button).toHaveClass("py-4");
      expect(button).toHaveClass("text-body-lg");
    });
  });

  it("applies fullWidth class when fullWidth prop is true", () => {
    render(<Button fullWidth>Full Width</Button>);
    const button = screen.getByRole("button", { name: /full width/i });
    expect(button).toHaveClass("w-full");
  });

  it("applies custom className", () => {
    render(<Button className="custom-class">Custom Class</Button>);
    const button = screen.getByRole("button", { name: /custom class/i });
    expect(button).toHaveClass("custom-class");
  });

  describe("Loading State", () => {
    it("shows loading spinner and disables button when loading is true", () => {
      render(<Button loading>Loading</Button>);
      const button = screen.getByRole("button", { name: /loading/i });
      expect(button).toBeDisabled();

      // Check for spinner (SVG)
      // We look for the SVG inside the button with the animate-spin class
      // Using querySelector on the button element is robust here
      // eslint-disable-next-line testing-library/no-node-access
      const spinner = button.querySelector("svg.animate-spin");
      expect(spinner).toBeInTheDocument();
    });

    it("does not show loading spinner when loading is false", () => {
      render(<Button loading={false}>Not Loading</Button>);
      const button = screen.getByRole("button", { name: /not loading/i });
      expect(button).not.toBeDisabled();

      // eslint-disable-next-line testing-library/no-node-access
      const spinner = button.querySelector("svg.animate-spin");
      expect(spinner).not.toBeInTheDocument();
    });
  });

  describe("Disabled State", () => {
    it("disables button when disabled prop is true", () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole("button", { name: /disabled/i });
      expect(button).toBeDisabled();
      expect(button).toHaveClass("disabled:cursor-not-allowed");
      expect(button).toHaveClass("disabled:opacity-50");
    });

    it("prevents click events when disabled", () => {
      const handleClick = jest.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      const button = screen.getByRole("button", { name: /disabled/i });
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  it("calls onClick handler when clicked", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    const button = screen.getByRole("button", { name: /click me/i });
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("forwards ref to the button element", () => {
    const ref = createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Ref Button</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    expect(ref.current).toHaveTextContent("Ref Button");
  });
});
