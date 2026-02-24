import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Select } from "./Select";
import { createRef } from "react";

describe("Select Component", () => {
  const options = [
    { value: "option1", label: "Option 1" },
    { value: "option2", label: "Option 2" },
    { value: "option3", label: "Option 3" },
  ];

  it("renders correctly with required props", () => {
    render(<Select options={options} data-testid="select" />);
    const selectElement = screen.getByTestId("select");
    expect(selectElement).toBeInTheDocument();
    expect(selectElement.tagName).toBe("SELECT");
    expect(screen.getAllByRole("option")).toHaveLength(3);
  });

  it("renders with a label and associates it correctly", () => {
    render(<Select label="Test Label" options={options} />);
    const labelElement = screen.getByText("Test Label");
    const selectElement = screen.getByLabelText("Test Label");
    expect(labelElement).toBeInTheDocument();
    expect(selectElement).toBeInTheDocument();
  });

  it("renders options correctly", () => {
    render(<Select options={options} />);
    options.forEach((option) => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
      expect(screen.getByRole("option", { name: option.label })).toHaveValue(option.value);
    });
  });

  it("calls onChange when an option is selected", async () => {
    const handleChange = jest.fn();
    render(<Select options={options} onChange={handleChange} />);
    const selectElement = screen.getByRole("combobox");

    await userEvent.selectOptions(selectElement, "option2");

    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(selectElement).toHaveValue("option2");
  });

  it("displays error message and applies error styles", () => {
    const errorMessage = "This field is required";
    render(<Select options={options} error={errorMessage} />);

    const errorElement = screen.getByText(errorMessage);
    expect(errorElement).toBeInTheDocument();
    expect(errorElement).toHaveClass("text-error");

    const selectElement = screen.getByRole("combobox");
    expect(selectElement).toHaveClass("border-error");
  });

  it("displays hint message when no error is present", () => {
    const hintMessage = "Select one option";
    render(<Select options={options} hint={hintMessage} />);

    const hintElement = screen.getByText(hintMessage);
    expect(hintElement).toBeInTheDocument();
    expect(hintElement).toHaveClass("text-text-muted");
  });

  it("does not display hint when error is present", () => {
    const hintMessage = "Select one option";
    const errorMessage = "Error occurred";
    render(<Select options={options} hint={hintMessage} error={errorMessage} />);

    expect(screen.queryByText(hintMessage)).not.toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("is disabled when disabled prop is true", () => {
    render(<Select options={options} disabled />);
    const selectElement = screen.getByRole("combobox");
    expect(selectElement).toBeDisabled();
  });

  it("forwards ref to the select element", () => {
    const ref = createRef<HTMLSelectElement>();
    render(<Select options={options} ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLSelectElement);
  });

  it("applies custom className", () => {
    render(<Select options={options} className="custom-class" data-testid="select" />);
    const selectElement = screen.getByTestId("select");
    expect(selectElement).toHaveClass("custom-class");
  });
});
