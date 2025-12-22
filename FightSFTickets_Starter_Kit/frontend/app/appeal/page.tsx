"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function AppealPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";

  const [formData, setFormData] = useState({
    citationNumber: "",
    licensePlate: "",
    violationDate: "",
    vehicleInfo: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.citationNumber.trim()) {
      newErrors.citationNumber = "Citation number is required";
    } else if (!/^\d{9}$/.test(formData.citationNumber.replace(/\D/g, ""))) {
      newErrors.citationNumber =
        "Citation number must be 9 digits (SF citations start with 9)";
    }

    if (!formData.violationDate) {
      newErrors.violationDate = "Violation date is required";
    }

    if (!formData.vehicleInfo.trim()) {
      newErrors.vehicleInfo = "Vehicle description is required";
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
      const { validateCitation } = await import("../lib/api");
      const result = await validateCitation({
        citation_number: formData.citationNumber,
        license_plate: formData.licensePlate || undefined,
        violation_date: formData.violationDate,
      });

      if (!result.is_valid) {
        setErrors({
          citationNumber: result.error_message || "Invalid citation",
        });
        setIsSubmitting(false);
        return;
      }

      if (result.is_past_deadline) {
        setErrors({
          citationNumber: "This citation is past the appeal deadline.",
        });
        setIsSubmitting(false);
        return;
      }

      // TODO: Store form data in context
      router.push(`/appeal/camera?type=${appealType}`);
    } catch (error) {
      console.error("Error validating citation:", error);
      setErrors({
        citationNumber: "Failed to validate citation. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
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
            {appealType === "certified" ? "Certified Mail ($19)" : "Standard Mail ($9)"}
          </span>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
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
                handleChange(
                  "citationNumber",
                  e.target.value.replace(/\D/g, "").slice(0, 9)
                )
              }
              placeholder="912345678"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                errors.citationNumber ? "border-red-500" : "border-gray-300"
              }`}
              maxLength={9}
            />
            {errors.citationNumber && (
              <p className="text-red-500 text-sm mt-1">{errors.citationNumber}</p>
            )}
            <p className="text-gray-500 text-sm mt-1">
              Found on your parking ticket (9-digit number starting with 9)
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
                handleChange("licensePlate", e.target.value.toUpperCase().slice(0, 10))
              }
              placeholder="ABC1234"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
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
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
                errors.violationDate ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.violationDate && (
              <p className="text-red-500 text-sm mt-1">{errors.violationDate}</p>
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
              Vehicle Description <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="vehicleInfo"
              value={formData.vehicleInfo}
              onChange={(e) =>
                handleChange("vehicleInfo", e.target.value.slice(0, 200))
              }
              placeholder="e.g., 2020 Honda Civic, Blue"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ${
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

        {/* UPL Disclaimer */}
        <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> We do not recommend specific evidence or
            promise outcomes. You are responsible for the content of your appeal.
          </p>
        </div>
      </div>
    </div>
  );
}

