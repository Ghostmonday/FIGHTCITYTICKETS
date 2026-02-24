import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CameraPage from "./page";
import { useAppeal } from "../../lib/appeal-context";
import { extractTextFromImage } from "../../lib/ocr-helper";
import { useRouter } from "next/navigation";

// Mock dependencies
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

jest.mock("../../lib/appeal-context", () => ({
  useAppeal: () => ({
    state: { photos: [], citationNumber: "" },
    updateState: jest.fn(),
  }),
}));

jest.mock("../../lib/ocr-helper", () => ({
  extractTextFromImage: jest.fn(),
}));

describe("CameraPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: jest.fn() });
  });

  const uploadFile = async (container: Element) => {
    const fileInput = container.querySelector('input[type="file"]');
    if (!fileInput) throw new Error("File input not found");
    const file = new File(["(⌐□_□)"], "citation.png", { type: "image/png" });
    await userEvent.upload(fileInput, file);
    return file;
  };

  it("displays an error message when OCR fails to detect a citation number", async () => {
    // Mock OCR failure
    (extractTextFromImage as jest.Mock).mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "some random text",
    });

    const { container } = render(<CameraPage />);
    await uploadFile(container);

    await waitFor(() => {
      expect(screen.getByText(/Citation not detected/i)).toBeInTheDocument();
    });
  });

  it("allows user to retake photo when OCR fails", async () => {
    (extractTextFromImage as jest.Mock).mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "some random text",
    });

    const { container } = render(<CameraPage />);
    await uploadFile(container);

    await waitFor(() => {
      expect(screen.getByText(/Citation not detected/i)).toBeInTheDocument();
    });

    // Click "Retake Photo"
    const retakeButton = screen.getByRole("button", { name: /Retake Photo/i });
    fireEvent.click(retakeButton);

    // Photo should be removed (Evidence 1 alt text gone)
    await waitFor(() => {
      expect(screen.queryByAltText(/Evidence 1/i)).not.toBeInTheDocument();
    });

    // Error message should be gone
    expect(screen.queryByText(/Citation not detected/i)).not.toBeInTheDocument();
  });

  it("allows user to enter manually when OCR fails", async () => {
    (extractTextFromImage as jest.Mock).mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "some random text",
    });

    const { container } = render(<CameraPage />);
    await uploadFile(container);

    await waitFor(() => {
      expect(screen.getByText(/Citation not detected/i)).toBeInTheDocument();
    });

    // Manual input should not be visible initially (or rather, the input field itself)
    // The "Enter citation number manually" button exists, but the input is hidden until clicked?
    // Let's check the implementation.
    // <button onClick={() => setShowManualInput(!showManualInput)}>...
    // {showManualInput && ( <input ... /> )}

    expect(screen.queryByPlaceholderText(/e.g., A12345678/i)).not.toBeInTheDocument();

    // Click "Enter Manually" from the error block
    const enterManuallyButton = screen.getAllByRole("button", { name: /Enter Manually/i }).find(
      btn => btn.closest('.border-red-200') || btn.className.includes('hover:bg-gray-50') // Identify the one in error block
    );

    // Actually, "Enter Manually" text is unique to the error block button?
    // The main button says "Enter citation number manually" (different text).
    // So "Enter Manually" is unique.

    const errorBlockButton = screen.getByRole("button", { name: /^Enter Manually$/i });
    fireEvent.click(errorBlockButton);

    // Manual input should now be visible
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/e.g., A12345678/i)).toBeInTheDocument();
    });
  });
});
