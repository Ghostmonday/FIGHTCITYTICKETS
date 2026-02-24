import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { Input } from "./Input";

describe("Input Component", () => {
  it("renders with default props", () => {
    render(<Input placeholder="Enter text" />);
    const input = screen.getByPlaceholderText("Enter text");
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass("border-border");
  });

  it("renders with a label and associates it correctly", () => {
    render(<Input label="Username" />);
    const label = screen.getByText("Username");
    const input = screen.getByLabelText("Username");

    expect(label).toBeInTheDocument();
    expect(input).toBeInTheDocument();
    expect(label).toHaveAttribute("for", input.id);
  });

  it("uses provided id for label association", () => {
    render(<Input label="Username" id="custom-id" />);
    const label = screen.getByText("Username");
    const input = screen.getByLabelText("Username");

    expect(input).toHaveAttribute("id", "custom-id");
    expect(label).toHaveAttribute("for", "custom-id");
  });

  it("renders error message and applies error styles", () => {
    const errorMessage = "Invalid input";
    render(<Input error={errorMessage} />);

    const error = screen.getByText(errorMessage);
    const input = screen.getByRole("textbox");

    expect(error).toBeInTheDocument();
    expect(error).toHaveClass("text-error");
    expect(input).toHaveClass("border-error");
  });

  it("applies success styles when success prop is true", () => {
    render(<Input success />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("border-success");
  });

  it("renders hint message when provided and no error", () => {
    const hintText = "This is a hint";
    render(<Input hint={hintText} />);
    const hint = screen.getByText(hintText);
    expect(hint).toBeInTheDocument();
    expect(hint).toHaveClass("text-text-muted");
  });

  it("does not render hint when error is present", () => {
    const hintText = "This is a hint";
    const errorText = "This is an error";
    render(<Input hint={hintText} error={errorText} />);

    expect(screen.queryByText(hintText)).not.toBeInTheDocument();
    expect(screen.getByText(errorText)).toBeInTheDocument();
  });

  it("handles user typing", () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Hello" } });

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(input).toHaveValue("Hello");
  });

  it("forwards ref to the input element", () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it("merges custom className", () => {
    render(<Input className="custom-class" />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("custom-class");
    expect(input).toHaveClass("bg-bg-surface"); // verify default classes are still there
  });

  it("passes disabled attribute", () => {
    render(<Input disabled />);
    const input = screen.getByRole("textbox");
    expect(input).toBeDisabled();
  });

  it("generates id from label if not provided", () => {
     render(<Input label="First Name" />);
     const input = screen.getByLabelText("First Name");
     expect(input.id).toBe("first-name");
  });
});
