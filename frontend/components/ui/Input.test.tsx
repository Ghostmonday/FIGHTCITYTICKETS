import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Input } from "./Input";
import React from "react";

describe("Input Component", () => {
  it("renders with default props", () => {
    render(<Input />);
    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass("border-border");
  });

  it("renders with a label and associates it with the input", () => {
    render(<Input label="Username" />);
    const label = screen.getByText("Username");
    const input = screen.getByLabelText("Username");
    expect(label).toBeInTheDocument();
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("id", "username");
  });

  it("uses custom id if provided", () => {
    render(<Input label="Username" id="custom-id" />);
    const input = screen.getByLabelText("Username");
    expect(input).toHaveAttribute("id", "custom-id");
  });

  it("renders with error state and message", () => {
    const errorMessage = "This field is required";
    render(<Input error={errorMessage} />);
    const input = screen.getByRole("textbox");
    const errorText = screen.getByText(errorMessage);

    expect(input).toHaveClass("border-error");
    expect(errorText).toBeInTheDocument();
    expect(errorText).toHaveClass("text-error");
  });

  it("renders with success state", () => {
    render(<Input success />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("border-success");
  });

  it("renders with a hint when no error is present", () => {
    const hintMessage = "Enter your username";
    render(<Input hint={hintMessage} />);
    const hintText = screen.getByText(hintMessage);
    expect(hintText).toBeInTheDocument();
    expect(hintText).toHaveClass("text-text-muted");
  });

  it("does not render hint when error is present", () => {
    const hintMessage = "Enter your username";
    const errorMessage = "Error occurred";
    render(<Input hint={hintMessage} error={errorMessage} />);

    expect(screen.queryByText(hintMessage)).not.toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("handles user input correctly", async () => {
    const user = userEvent.setup();
    render(<Input />);
    const input = screen.getByRole("textbox");

    await user.type(input, "Hello World");
    expect(input).toHaveValue("Hello World");
  });

  it("forwards ref to the input element", () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it("merges custom className with default styles", () => {
    render(<Input className="custom-class" />);
    const input = screen.getByRole("textbox");
    expect(input).toHaveClass("custom-class");
    expect(input).toHaveClass("w-full"); // Default class
  });

  it("passes other props to the input element", () => {
    render(<Input placeholder="Enter text" disabled data-testid="test-input" />);
    const input = screen.getByTestId("test-input");
    expect(input).toHaveAttribute("placeholder", "Enter text");
    expect(input).toBeDisabled();
  });
});
