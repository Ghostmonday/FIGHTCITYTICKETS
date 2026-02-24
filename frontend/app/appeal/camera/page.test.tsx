import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import CameraPage from "./page";

// Mock dependencies
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

const mockUpdateState = jest.fn();

jest.mock("../../lib/appeal-context", () => ({
  useAppeal: () => ({
    state: { photos: [], citationNumber: "" },
    updateState: mockUpdateState,
  }),
}));

// Mock OCR helper
const mockExtractTextFromImage = jest.fn();
jest.mock("../../lib/ocr-helper", () => ({
  extractTextFromImage: (...args: any[]) => mockExtractTextFromImage(...args),
}));

// Mock S3 upload
jest.mock("../../lib/s3-upload", () => ({
  uploadPhoto: jest.fn().mockResolvedValue({ is_s3: false, url: "test-url" }),
}));

describe("CameraPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("displays an error message when OCR fails to detect a citation number", async () => {
    // Mock OCR returning no citation number
    mockExtractTextFromImage.mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "Some random text",
    });

    const { container } = render(<CameraPage />);

    // Simulate file upload
    const file = new File(["(⌐□_□)"], "test.png", { type: "image/png" });
    const input = container.querySelector('input[type="file"]');

    if (!input) throw new Error("File input not found");

    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    // Wait for error to appear
    await waitFor(() => {
        expect(screen.getByText(/Citation not detected/i)).toBeInTheDocument();
        expect(screen.getByText(/Could not read citation number/i)).toBeInTheDocument();
    });
  });

  it("removes the photo when 'Retake Photo' is clicked after OCR failure", async () => {
    mockExtractTextFromImage.mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "Some random text",
    });

    const { container } = render(<CameraPage />);

    const file = new File(["(⌐□_□)"], "test.png", { type: "image/png" });
    const input = container.querySelector('input[type="file"]');

    if (!input) throw new Error("File input not found");

    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    await waitFor(() => {
        expect(screen.getByText(/Retake Photo/i)).toBeInTheDocument();
    });

    // Click Retake Photo
    fireEvent.click(screen.getByText(/Retake Photo/i));

    // Verify photo is removed (and thus the error message too)
    await waitFor(() => {
        expect(screen.queryByText(/Citation not detected/i)).not.toBeInTheDocument();
        expect(screen.queryByAltText(/Evidence 1/i)).not.toBeInTheDocument();
    });
  });

  it("shows manual input when 'Enter Manually' is clicked", async () => {
    mockExtractTextFromImage.mockResolvedValue({
      citationNumber: undefined,
      confidence: 0,
      rawText: "Some random text",
    });

    const { container } = render(<CameraPage />);

    const file = new File(["(⌐□_□)"], "test.png", { type: "image/png" });
    const input = container.querySelector('input[type="file"]');

    if (!input) throw new Error("File input not found");

    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    await waitFor(() => {
        expect(screen.getByText(/Enter Manually/i)).toBeInTheDocument();
    });

    // Click Enter Manually
    fireEvent.click(screen.getByText(/Enter Manually/i));

    // Verify input is shown
    // The placeholder is "e.g., A12345678"
    expect(screen.getByPlaceholderText(/e.g., A12345678/i)).toBeInTheDocument();
  });
});
