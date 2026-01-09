"use client";

import { useEffect, useRef, useState } from "react";

interface AddressAutocompleteProps {
  value: string;
  onChange: (address: {
    addressLine1: string;
    addressLine2?: string;
    city: string;
    state: string;
    zip: string;
  }) => void;
  onError?: (error: string) => void;
  placeholder?: string;
  required?: boolean;
  className?: string;
}

// Google Maps types (loaded dynamically at runtime)
declare global {
  interface Window {
    google?: any;
    initGooglePlaces?: () => void;
  }
}

export default function AddressAutocomplete({
  value,
  onChange,
  onError,
  placeholder = "Enter your address",
  required = false,
  className = "",
}: AddressAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const autocompleteRef = useRef<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load Google Places API script
  useEffect(() => {
    // Check if already loaded
    if (window.google?.maps?.places) {
      setIsLoaded(true);
      setIsLoading(false);
      return;
    }

    // Check if script is already being loaded
    if (document.querySelector('script[src*="places"]')) {
      // Wait for it to load
      const checkInterval = setInterval(() => {
        if (window.google?.maps?.places) {
          setIsLoaded(true);
          setIsLoading(false);
          clearInterval(checkInterval);
        }
      }, 100);
      return () => clearInterval(checkInterval);
    }

    // Load the script
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setIsLoaded(true);
      setIsLoading(false);
    };
    script.onerror = () => {
      setIsLoading(false);
      onError?.("Failed to load address autocomplete. Please enter your address manually.");
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [onError]);

  // Initialize autocomplete when script loads
  useEffect(() => {
    if (!isLoaded || !inputRef.current) return;

    try {
      // Create autocomplete instance
      const autocomplete = new window.google.maps.places.Autocomplete(
        inputRef.current,
        {
          componentRestrictions: { country: "us" }, // US addresses only
          fields: ["address_components", "formatted_address"],
          types: ["address"], // Only addresses, not businesses
        }
      );

      autocompleteRef.current = autocomplete;

      // Handle place selection
      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();

        if (!place.address_components) {
          onError?.("Could not parse address. Please enter manually.");
          return;
        }

        // Parse address components
        let addressLine1 = "";
        let addressLine2 = "";
        let city = "";
        let state = "";
        let zip = "";

        place.address_components.forEach((component: any) => {
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
            state = component.short_name; // Use short form (CA, NY, etc.)
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

        // Update parent component
        onChange({
          addressLine1: addressLine1.trim(),
          addressLine2: addressLine2 || undefined,
          city,
          state,
          zip,
        });
      });
    } catch (error) {
      console.error("Error initializing Google Places:", error);
      onError?.("Address autocomplete unavailable. Please enter address manually.");
    }

    return () => {
      if (autocompleteRef.current) {
        window.google?.maps?.event?.clearInstanceListeners?.(autocompleteRef.current);
      }
    };
  }, [isLoaded, onChange, onError]);

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="text"
        value={value}
        placeholder={isLoading ? "Loading address autocomplete..." : placeholder}
        required={required}
        className={`w-full p-3 border rounded-lg ${className} ${
          isLoading ? "bg-gray-100" : ""
        }`}
        autoComplete="street-address"
      />
      {isLoading && (
        <div className="absolute right-3 top-3 text-xs text-gray-500">
          Loading...
        </div>
      )}
      {isLoaded && (
        <div className="absolute right-3 top-3 text-xs text-gray-400">
          ✓ Autocomplete enabled
        </div>
      )}
    </div>
  );
}

