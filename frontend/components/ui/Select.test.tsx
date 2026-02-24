import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Select } from "./Select";
import React from "react";

describe("Select Component", () => {
  const defaultOptions = [
    { value: "option1", label: "Option 1" },
    { value: "option2", label: "Option 2" },
    { value: "option3", label: "Option 3" },
  ];

  it("renders correctly with required props", () => {
    render(<Select options={defaultOptions} />);
    const select = screen.getByRole("combobox");
    expect(select).toBeInTheDocument();
    expect(select).toHaveClass("border-border");
  });

  it("renders with a label and associates it correctly", () => {
    render(<Select label="Test Label" options={defaultOptions} />);
    const label = screen.getByText("Test Label");
    const select = screen.getByRole("combobox");

    expect(label).toBeInTheDocument();
    expect(select).toBeInTheDocument();
    expect(label).toHaveAttribute("for", select.id);
  });

  it("renders all options", () => {
    render(<Select options={defaultOptions} />);
    const options = screen.getAllByRole("option");
    expect(options).toHaveLength(3);
    expect(options[0]).toHaveValue("option1");
    expect(options[0]).toHaveTextContent("Option 1");
    expect(options[1]).toHaveValue("option2");
    expect(options[1]).toHaveTextContent("Option 2");
    expect(options[2]).toHaveValue("option3");
    expect(options[2]).toHaveTextContent("Option 3");
  });

  it("calls onChange when an option is selected", async () => {
    const handleChange = jest.fn();
    render(<Select options={defaultOptions} onChange={handleChange} />);

    const select = screen.getByRole("combobox");
    const user = userEvent.setup();

    await user.selectOptions(select, "option2");

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(select).toHaveValue("option2");
  });

  it("displays error message and applies error styles", () => {
    const errorMessage = "This field is required";
    render(<Select options={defaultOptions} error={errorMessage} />);

    const error = screen.getByText(errorMessage);
    const select = screen.getByRole("combobox");

    expect(error).toBeInTheDocument();
    expect(error).toHaveClass("text-error");
    expect(select).toHaveClass("border-error");
  });

  it("displays hint message when no error is present", () => {
    const hintMessage = "Please select an option";
    render(<Select options={defaultOptions} hint={hintMessage} />);

    const hint = screen.getByText(hintMessage);
    expect(hint).toBeInTheDocument();
    expect(hint).toHaveClass("text-text-muted");
  });

  it("does not display hint when error is present", () => {
    const hintMessage = "Please select an option";
    const errorMessage = "Error occurred";
    render(<Select options={defaultOptions} hint={hintMessage} error={errorMessage} />);

    const error = screen.getByText(errorMessage);
    const hint = screen.queryByText(hintMessage);

    expect(error).toBeInTheDocument();
    expect(hint).not.toBeInTheDocument();
  });

  it("renders in disabled state", () => {
    render(<Select options={defaultOptions} disabled />);
    const select = screen.getByRole("combobox");
    expect(select).toBeDisabled();
  });

  it("forwards ref to the select element", () => {
    const ref = React.createRef<HTMLSelectElement>();
    render(<Select options={defaultOptions} ref={ref} />);

    expect(ref.current).toBeInstanceOf(HTMLSelectElement);
  });

  it("uses provided id if available", () => {
      render(<Select options={defaultOptions} id="custom-id" label="Test Label" />);
      const select = screen.getByRole("combobox");
      expect(select).toHaveAttribute("id", "custom-id");
  });

  it("generates id from label if id is not provided", () => {
      render(<Select options={defaultOptions} label="Test Label" />);
      const select = screen.getByRole("combobox");
      expect(select).toHaveAttribute("id", "test-label");
  });
});
