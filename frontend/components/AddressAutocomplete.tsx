"use client";

import { useEffect, useRef, useState } from "react";
import { error as logError } from "@/lib/logger";

interface AddressAutocompleteProps {
  value: string;
  onChange: (address: {
    addressLine1: string;
    addressLine2?: string;
    city: string;
    state: string;
    zip: string;
  }) => void;
  onInputChange?: (value: string) => void; // For manual input changes
  onError?: (error: string) => void;
  placeholder?: string;
  required?: boolean;
  className?: string;
  enableAutocomplete?: boolean; // Allow parent to control autocomplete
}

// Session token for Google Places billing (rotated periodically)
let sessionToken: string | null = null;

function generateSessionToken(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export default function AddressAutocomplete({
  value,
  onChange,
  onInputChange,
  onError,
  placeholder = "Enter your address",
  required = false,
  className = "",
  enableAutocomplete = true, // Default to enabled
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [suggestions, setSuggestions] = useState<Array<{ place_id: string; description: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAutocompleting, setIsAutocompleting] = useState(false);
  const [useAutocomplete, setUseAutocomplete] = useState(enableAutocomplete);
  const [addressVerified, setAddressVerified] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Initialize session token and load Google Maps API (only if autocomplete is enabled)
  useEffect(() => {
    if (!useAutocomplete) {
      setIsLoading(false);
      return;
    }

    sessionToken = generateSessionToken();

    // Check if Google Maps API is already loaded
    if (window.google?.maps?.places) {
      setIsLoading(false);
      return;
    }

    // Only load Google Maps API if autocomplete is enabled and API key exists
    if (!process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY) {
      setIsLoading(false);
      setUseAutocomplete(false); // Disable autocomplete if no API key
      return;
    }

    // Load the script
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setIsLoading(false);
    };
    script.onerror = () => {
      setIsLoading(false);
      setUseAutocomplete(false); // Fallback to manual entry if script fails
      onError?.(
        "Autocomplete unavailable. You can enter your address manually."
      );
    };
    document.head.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [useAutocomplete, onError]);

  // Fetch address suggestions via backend proxy to protect API key
  const fetchSuggestions = async (input: string) => {
    if (!useAutocomplete || !input || input.length < 3) {
      setSuggestions([]);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      setIsAutocompleting(true);
      const response = await fetch(`/places/autocomplete?input=${encodeURIComponent(input)}`, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error("Failed to fetch suggestions");
      }

      const data = await response.json();
      setSuggestions(data.predictions || []);
    } catch (error) {
      if (error instanceof Error && error.name !== "AbortError") {
        // Silently fail - user can still type manually
        setSuggestions([]);
      }
    } finally {
      setIsAutocompleting(false);
    }
  };

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    
    // If manual mode, just pass the value to parent
    if (!useAutocomplete) {
      onInputChange?.(input);
      return;
    }
    
    // If autocomplete mode, trigger suggestions
    onInputChange?.(input); // Still notify parent of input changes
    // Debounce the API call
    const timeoutId = setTimeout(() => {
      fetchSuggestions(input);
    }, 300);
    return () => clearTimeout(timeoutId);
  };

  // Handle place selection
  const handleSelectPlace = async (placeId: string) => {
    // Fetch place details via backend proxy
    try {
      setIsLoading(true);
      const response = await fetch(
        `/places/details?place_id=${placeId}&session_token=${sessionToken}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch place details");
      }

      const data = await response.json();

      if (!data.result || !data.result.address_components) {
        onError?.("Could not parse address. Please enter manually.");
        return;
      }

      // Parse address components
      let addressLine1 = "";
      let addressLine2 = "";
      let city = "";
      let state = "";
      let zip = "";

      data.result.address_components.forEach((component: any) => {
        const types = component.types;

        if (types.includes("street_number")) {
          addressLine1 = component.long_name + " ";
        }
        if (types.includes("route")) {
          addressLine1 += component.long_name;
        }
        if (types.includes("subpremise")) {
          addressLine2 = component.long_name;
        }
        if (types.includes("locality")) {
          city = component.long_name;
        }
        if (types.includes("administrative_area_level_1")) {
          state = component.short_name;
        }
        if (types.includes("postal_code")) {
          zip = component.long_name;
        }
      });

      // Validate we got the essential components
      if (!addressLine1.trim() || !city || !state || !zip) {
        onError?.("Incomplete address. Please verify and complete manually.");
        return;
      }

      // Update parent component with parsed address
      onChange({
        addressLine1: addressLine1.trim(),
        addressLine2: addressLine2 || undefined,
        city,
        state,
        zip,
      });

      // Show verification success
      setAddressVerified(true);
      setTimeout(() => setAddressVerified(false), 3000); // Hide after 3 seconds

      // Clear suggestions
      setSuggestions([]);
      sessionToken = generateSessionToken();
    } catch (error) {
      logError("Error fetching place details:", error);
      onError?.("Failed to get address details. Please enter manually.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          placeholder={
            useAutocomplete
              ? isLoading
                ? "Loading address verification..."
                : "Start typing to verify your address"
              : "Enter your complete address"
          }
          required={required}
          className={`w-full p-3 border rounded-lg pr-24 ${className} ${
            isLoading ? "bg-gray-100" : ""
          }`}
          autoComplete="street-address"
          onChange={handleInputChange}
        />
        {process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY && (
          <button
            type="button"
            onClick={() => {
              setUseAutocomplete(!useAutocomplete);
              setSuggestions([]); // Clear suggestions when toggling
              setAddressVerified(false); // Reset verification status
            }}
            className={`absolute right-2 top-1/2 -translate-y-1/2 text-xs whitespace-nowrap px-2 py-1 bg-white rounded border transition-colors ${
              useAutocomplete
                ? "text-green-700 border-green-300 hover:bg-green-50"
                : "text-blue-600 border-blue-300 hover:bg-blue-50"
            }`}
            title={
              useAutocomplete
                ? "Address verification enabled - Click to switch to manual entry"
                : "Click to enable instant address verification"
            }
          >
            {useAutocomplete ? "✓ Verified" : "Verify"}
          </button>
        )}
        {useAutocomplete && isAutocompleting && (
          <div className="absolute right-16 top-1/2 -translate-y-1/2 text-xs text-gray-500">
            Loading...
          </div>
        )}
      </div>
      {useAutocomplete && suggestions.length > 0 && (
        <ul className="absolute z-10 w-full bg-white border rounded-lg shadow-lg mt-1 max-h-60 overflow-auto">
          {suggestions.map((suggestion) => (
            <li
              key={suggestion.place_id}
              className="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
              onClick={() => handleSelectPlace(suggestion.place_id)}
            >
              {suggestion.description}
            </li>
          ))}
        </ul>
      )}
      {!useAutocomplete && (
        <p className="text-xs text-blue-600 mt-1">
          ✨ Click "Auto" to verify your address instantly with autocomplete
        </p>
      )}
      {useAutocomplete && addressVerified && (
        <p className="text-xs text-green-600 mt-1 font-medium animate-pulse">
          ✓ Address verified and validated! Your mail will be delivered correctly.
        </p>
      )}
      {useAutocomplete && !addressVerified && (
        <p className="text-xs text-green-600 mt-1">
          ✓ Verification enabled - select an address to auto-verify
        </p>
      )}
    </div>
  );
}
