"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "../lib/appeal-context";
import { validateCitation } from "../lib/api";

function AppealPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType =
    (searchParams.get("type") as "standard" | "certified") || "standard";
  const { state, updateState } = useAppeal();

  const [formData, setFormData] = useState({
    citationNumber: state.citationNumber || "",
    licensePlate: state.licensePlate || "",
    violationDate: state.violationDate || "",
    vehicleInfo: state.vehicleInfo || "",
  });

  // Keep local state in sync if context changes externally (optional, but good practice)
  useEffect(() => {
    setFormData((prev) => ({
      ...prev,
      citationNumber: state.citationNumber || prev.citationNumber,
      licensePlate: state.licensePlate || prev.licensePlate,
      violationDate: state.violationDate || prev.violationDate,
      vehicleInfo: state.vehicleInfo || prev.vehicleInfo,
    }));
  }, [state]);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationWarning, setValidationWarning] = useState<string | null>(
    null,
  );
  const [bypassValidation, setBypassValidation] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.citationNumber.trim()) {
      newErrors.citationNumber = "Citation number is required";
    } else if (formData.citationNumber.trim().length < 5) {
      newErrors.citationNumber = "Citation number seems too short";
    }

    if (!formData.violationDate) {
      newErrors.violationDate = "Violation date is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Validate citation and get agency information
      const validationResponse = await validateCitation({
        citation_number: formData.citationNumber,
        license_plate: formData.licensePlate || undefined,
        violation_date: formData.violationDate,
      });

      if (!validationResponse.is_valid) {
        setErrors({
          citationNumber:
            validationResponse.error_message || "Invalid citation number",
        });
        setIsSubmitting(false);
        return;
      }

      // Update state with citation data and agency
      updateState({
        citationNumber: formData.citationNumber,
        violationDate: formData.violationDate,
        licensePlate: formData.licensePlate,
        vehicleInfo: formData.vehicleInfo,
        appealType: appealType,
        agency: validationResponse.agency,
      });

      router.push(`/appeal/camera?type=${appealType}`);
    } catch (error) {
      console.error("Citation validation error:", error);
      setErrors({
        citationNumber: "Failed to validate citation. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error and warning when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
    if (validationWarning) {
      setValidationWarning(null);
      setBypassValidation(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Home
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Enter Your Citation Information
          </h1>
          <p className="text-gray-600 mt-2">
            Step 1 of 5: Provide your parking ticket details
          </p>
        </div>

        {/* Service Type Badge */}
        <div className="mb-6">
          <span
            className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${
              appealType === "certified"
                ? "bg-indigo-100 text-indigo-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {appealType === "certified"
              ? "Certified Mail ($19)"
              : "Standard Mail ($9)"}
          </span>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-lg shadow-md p-6"
        >
          {/* Citation Number */}
          <div className="mb-6">
            <label
              htmlFor="citationNumber"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Citation Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="citationNumber"
              value={formData.citationNumber}
              onChange={(e) =>
                handleChange("citationNumber", e.target.value.slice(0, 15))
              }
              placeholder="Enter your citation number"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 ${
                errors.citationNumber ? "border-red-500" : "border-gray-300"
              }`}
              maxLength={15}
            />
            {errors.citationNumber && (
              <p className="text-red-500 text-sm mt-1">
                {errors.citationNumber}
              </p>
            )}
            <p className="text-gray-500 text-sm mt-1">
              Found on your parking ticket
            </p>
          </div>

          {/* License Plate */}
          <div className="mb-6">
            <label
              htmlFor="licensePlate"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              License Plate (Optional)
            </label>
            <input
              type="text"
              id="licensePlate"
              value={formData.licensePlate}
              onChange={(e) =>
                handleChange(
                  "licensePlate",
                  e.target.value.toUpperCase().slice(0, 10),
                )
              }
              placeholder="ABC1234"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
              maxLength={10}
            />
            <p className="text-gray-500 text-sm mt-1">
              Helps verify your citation
            </p>
          </div>

          {/* Violation Date */}
          <div className="mb-6">
            <label
              htmlFor="violationDate"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Violation Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="violationDate"
              value={formData.violationDate}
              onChange={(e) => handleChange("violationDate", e.target.value)}
              max={new Date().toISOString().split("T")[0]}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 ${
                errors.violationDate ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.violationDate && (
              <p className="text-red-500 text-sm mt-1">
                {errors.violationDate}
              </p>
            )}
            <p className="text-gray-500 text-sm mt-1">
              The date you received the parking ticket
            </p>
          </div>

          {/* Vehicle Info */}
          <div className="mb-6">
            <label
              htmlFor="vehicleInfo"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Vehicle Description (Optional)
            </label>
            <input
              type="text"
              id="vehicleInfo"
              value={formData.vehicleInfo}
              onChange={(e) =>
                handleChange("vehicleInfo", e.target.value.slice(0, 200))
              }
              placeholder="e.g., 2020 Honda Civic, Blue"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 ${
                errors.vehicleInfo ? "border-red-500" : "border-gray-300"
              }`}
              maxLength={200}
            />
            {errors.vehicleInfo && (
              <p className="text-red-500 text-sm mt-1">{errors.vehicleInfo}</p>
            )}
            <p className="text-gray-500 text-sm mt-1">
              Make, model, and color of your vehicle
            </p>
          </div>

          {/* Validation Warning with Bypass */}
          {validationWarning && (
            <div className="mb-6 bg-amber-50 border border-amber-300 rounded-lg p-4">
              <div className="flex items-start">
                <svg
                  className="w-5 h-5 text-amber-500 mt-0.5 mr-3 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="flex-1">
                  <p className="text-amber-800 text-sm">{validationWarning}</p>
                  <button
                    type="button"
                    onClick={() => {
                      setBypassValidation(true);
                      setValidationWarning(null);
                    }}
                    className="mt-3 text-sm font-medium text-amber-700 hover:text-amber-900 underline"
                  >
                    Continue Anyway →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-4">
            <Link
              href="/"
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium text-center hover:bg-gray-50 transition-colors"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Validating..." : "Continue →"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function AppealPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AppealPageContent />
    </Suspense>
  );
}
