import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import AddressAutocomplete from "./AddressAutocomplete";

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock environment variable
const originalEnv = process.env;

describe("AddressAutocomplete", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env = { ...originalEnv, NEXT_PUBLIC_GOOGLE_PLACES_API_KEY: "test-key" };
    // Default fetch mock
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ predictions: [] }),
    });
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  const mockOnChange = jest.fn();

  it("renders input with loading state initially and then ready state", async () => {
    const scriptMock = {
      src: "",
      async: false,
      defer: false,
      onload: null as (() => void) | null,
      onerror: null as (() => void) | null,
    };

    const originalCreateElement = document.createElement.bind(document);
    const createElementSpy = jest.spyOn(document, "createElement").mockImplementation((tagName, options) => {
        if (tagName === "script") {
            return scriptMock as unknown as HTMLScriptElement;
        }
        return originalCreateElement(tagName, options);
    });

    const appendChildSpy = jest.spyOn(document.head, "appendChild").mockImplementation((node) => node);
    const removeChildSpy = jest.spyOn(document.head, "removeChild").mockImplementation((node) => node);

    const { unmount } = render(<AddressAutocomplete value="" onChange={mockOnChange} />);

    // Initially loading
    expect(screen.getByPlaceholderText("Loading address verification...")).toBeInTheDocument();

    // Trigger script load
    act(() => {
        if (scriptMock.onload) scriptMock.onload();
    });

    // Now ready
    expect(screen.getByPlaceholderText("Start typing to verify your address")).toBeInTheDocument();

    unmount();
    createElementSpy.mockRestore();
    appendChildSpy.mockRestore();
    removeChildSpy.mockRestore();
  });

  it("switches to manual entry when toggle is clicked", async () => {
      // Mock script load immediately
      const originalCreateElement = document.createElement.bind(document);
      const createElementSpy = jest.spyOn(document, "createElement").mockImplementation((tagName, options) => {
        if (tagName === "script") {
             const script: any = { src: "", async: true, defer: true, onload: null };
             setTimeout(() => script.onload && script.onload(), 0);
             return script;
        }
        return originalCreateElement(tagName, options);
    });
    jest.spyOn(document.head, "appendChild").mockImplementation((node) => node);

    render(<AddressAutocomplete value="" onChange={mockOnChange} />);

    // Wait for loading to finish
    await waitFor(() => expect(screen.getByPlaceholderText("Start typing to verify your address")).toBeInTheDocument());

    const toggleButton = screen.getByText("✓ Verified");
    fireEvent.click(toggleButton);

    expect(screen.getByPlaceholderText("Enter your complete address")).toBeInTheDocument();
    expect(screen.getByText("Verify")).toBeInTheDocument();

    jest.restoreAllMocks();
  });

  it("fetches suggestions on input", async () => {
    jest.useFakeTimers();

    // Capture the script so we can trigger load synchronously
    let scriptEl: any;
    const originalCreateElement = document.createElement.bind(document);
    const createElementSpy = jest.spyOn(document, "createElement").mockImplementation((tagName, options) => {
         if (tagName === "script") {
             scriptEl = { src: "", async: true, defer: true, onload: null };
             return scriptEl;
         }
         return originalCreateElement(tagName, options);
    });
    jest.spyOn(document.head, "appendChild").mockImplementation((node) => node);

    render(<AddressAutocomplete value="" onChange={mockOnChange} />);

    // Trigger script load
    act(() => {
        if (scriptEl && scriptEl.onload) scriptEl.onload();
    });

    const input = screen.getByPlaceholderText("Start typing to verify your address");

    fireEvent.change(input, { target: { value: "123 Main" } });

    // Fast forward debounce
    await act(async () => {
        jest.advanceTimersByTime(300);
    });

    expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/places/autocomplete?input=123%20Main"),
        expect.any(Object)
    );

    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it("selects a place and fetches details", async () => {
      // Setup ready state
      const originalCreateElement = document.createElement.bind(document);
      jest.spyOn(document, "createElement").mockImplementation((tagName, options) => {
        if (tagName === "script") {
             const script: any = { src: "", async: true, defer: true, onload: null };
             setTimeout(() => script.onload && script.onload(), 0);
             return script;
        }
        return originalCreateElement(tagName, options);
    });
    jest.spyOn(document.head, "appendChild").mockImplementation((node) => node);

    // Mock suggestions response
    mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            predictions: [
                { place_id: "place123", description: "123 Main St, Springfield" }
            ]
        })
    });

    render(<AddressAutocomplete value="" onChange={mockOnChange} />);
    await waitFor(() => expect(screen.getByPlaceholderText("Start typing to verify your address")).toBeInTheDocument());

    const input = screen.getByPlaceholderText("Start typing to verify your address");
    fireEvent.change(input, { target: { value: "123 Main" } });

    // Wait for debounce and fetch
    // Note: Since we didn't use fake timers here, we rely on waitFor to wait for the real timeout (300ms)
    await waitFor(() => expect(mockFetch).toHaveBeenCalled(), { timeout: 1000 });

    // Suggestions should appear
    await waitFor(() => expect(screen.getByText("123 Main St, Springfield")).toBeInTheDocument());

    // Mock details response for the next call
    mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
            result: {
                address_components: [
                    { types: ["street_number"], long_name: "123" },
                    { types: ["route"], long_name: "Main St" },
                    { types: ["locality"], long_name: "Springfield" },
                    { types: ["administrative_area_level_1"], short_name: "IL" },
                    { types: ["postal_code"], long_name: "62704" }
                ]
            }
        })
    });

    fireEvent.click(screen.getByText("123 Main St, Springfield"));

    await waitFor(() => expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/places/details?place_id=place123")
    ));

    expect(mockOnChange).toHaveBeenCalledWith({
        addressLine1: "123 Main St",
        addressLine2: undefined,
        city: "Springfield",
        state: "IL",
        zip: "62704"
    });

    jest.restoreAllMocks();
  });

  it("handles missing API key by disabling autocomplete", () => {
      process.env = { ...originalEnv, NEXT_PUBLIC_GOOGLE_PLACES_API_KEY: "" };

      render(<AddressAutocomplete value="" onChange={mockOnChange} />);

      // Should default to manual mode placeholder
      expect(screen.getByPlaceholderText("Enter your complete address")).toBeInTheDocument();
      // Verify button is missing or in verify mode?
      // If no API key, the Verify button is not rendered: {process.env... && <button>}
      expect(screen.queryByText("Verify")).not.toBeInTheDocument();
      expect(screen.queryByText("✓ Verified")).not.toBeInTheDocument();
  });
});
