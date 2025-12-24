"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "../../lib/appeal-context";

function CheckoutPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";
  const { state, updateState } = useAppeal();

  const [isLoading, setIsLoading] = useState(false);
  const [userInfo, setUserInfo] = useState({
    name: state.userInfo?.name || "",
    email: state.userInfo?.email || "",
    addressLine1: state.userInfo?.addressLine1 || "",
    addressLine2: state.userInfo?.addressLine2 || "",
    city: state.userInfo?.city || "",
    state: state.userInfo?.state || "",
    zip: state.userInfo?.zip || "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Agency display names
  const agencyDisplayNames: Record<string, string> = {
    SFMTA: "SFMTA (San Francisco Municipal Transportation Agency)",
    SFPD: "San Francisco Police Department",
    SFSU: "San Francisco State University",
    SFMUD: "San Francisco Municipal Utility District",
    UNKNOWN: "San Francisco Parking Citation Agency",
  };

  // Agency mailing addresses
  const agencyAddresses: Record<string, string> = {
    SFMTA: "1 South Van Ness Avenue, Floor 7\nSan Francisco, CA 94103",
    SFPD: "850 Bryant Street, Room 500\nSan Francisco, CA 94103",
    SFSU: "1600 Holloway Avenue, Burk Hall 100\nSan Francisco, CA 94132",
    SFMUD: "525 Golden Gate Avenue, 12th Floor\nSan Francisco, CA 94102",
    UNKNOWN: "1 South Van Ness Avenue, Floor 7\nSan Francisco, CA 94103",
  };

  const prices = {
    standard: { amount: 9.0, label: "Standard Mail" },
    certified: { amount: 19.0, label: "Certified Mail" },
  };

  const currentPrice =
    prices[appealType as keyof typeof prices] || prices.standard;

  // Get display name for agency
  const agencyDisplayName = agencyDisplayNames[state.agency || "UNKNOWN"];

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!userInfo.name.trim()) newErrors.name = "Full name is required";
    if (!userInfo.addressLine1.trim())
      newErrors.addressLine1 = "Address is required";
    if (!userInfo.city.trim()) newErrors.city = "City is required";
    if (!userInfo.state.trim() || userInfo.state.length !== 2)
      newErrors.state = "State code (2 letters) is required";
    if (!userInfo.zip.trim() || userInfo.zip.length !== 5)
      newErrors.zip = "Valid 5-digit ZIP code is required";
    if (!userInfo.email.trim() || !userInfo.email.includes("@"))
      newErrors.email = "Valid email is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCheckout = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    // Save user info to context
    updateState({ userInfo });

    try {
      const { createCheckoutSession } = await import("../../lib/api");

      const checkoutData = {
        citation_number: state.citationNumber || "912345678",
        appeal_type: appealType as "standard" | "certified",
        user_name: userInfo.name,
        user_address_line1: userInfo.addressLine1,
        user_address_line2: userInfo.addressLine2,
        user_city: userInfo.city,
        user_state: userInfo.state,
        user_zip: userInfo.zip,
        user_email: userInfo.email,
        violation_date: state.violationDate || "2024-01-15",
        vehicle_info: state.vehicleInfo || "Honda Civic",
        appeal_reason: state.transcript || "Sample reason",
        draft_text: state.draftLetter || "Sample draft text",
        license_plate: state.licensePlate,
        selected_evidence: state.photos,
        signature_data: state.signature || undefined,
      };

      const result = await createCheckoutSession(checkoutData);

      if (result.checkout_url) {
        window.location.href = result.checkout_url;
      } else {
        throw new Error("No checkout URL received");
      }
    } catch (error) {
      console.error("Checkout error:", error);
      alert(
        error instanceof Error
          ? error.message
          : "Failed to start checkout. Please try again.",
      );
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserInfo((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Review & Pay</h1>
          <p className="text-gray-600 mt-2">Complete your appeal submission</p>
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Order Summary
          </h2>

          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-700">Citation Agency</span>
              <span className="font-medium">{agencyDisplayName}</span>
            </div>
            <div className="flex justify-between items-start">
              <span className="text-gray-700">Mailing Address</span>
              <div className="text-right font-medium text-sm">
                <div className="whitespace-pre-line">
                  {agencyAddresses[state.agency || "UNKNOWN"]}
                </div>
                <p className="text-gray-500 text-xs mt-1">
                  Your appeal will be sent here
                </p>
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700">Citation Number</span>
              <span className="font-medium">
                {state.citationNumber || "Not provided"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700">Service Type</span>
              <span className="font-medium">{currentPrice.label}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700">Appeal Letter Generation</span>
              <span className="text-gray-600">Included</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700">Mail Delivery</span>
              <span className="text-gray-600">
                {appealType === "certified" ? "Certified" : "Standard"}
              </span>
            </div>
            <div className="border-t pt-4 flex justify-between text-lg font-bold">
              <span>Total</span>
              <span className="text-indigo-600">
                ${currentPrice.amount.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {/* Service Type Selection */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Change Service Type
          </h2>
          <div className="space-y-3">
            <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="serviceType"
                value="standard"
                checked={appealType === "standard"}
                onChange={() => router.push("/appeal/checkout?type=standard")}
                className="mr-3 text-indigo-600"
              />
              <div className="flex-1">
                <div className="font-medium">Standard Mail - $9.00</div>
                <div className="text-sm text-gray-600">
                  Regular mail delivery (~$1 cost)
                </div>
              </div>
            </label>
            <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="serviceType"
                value="certified"
                checked={appealType === "certified"}
                onChange={() => router.push("/appeal/checkout?type=certified")}
                className="mr-3 text-indigo-600"
              />
              <div className="flex-1">
                <div className="font-medium">Certified Mail - $19.00</div>
                <div className="text-sm text-gray-600">
                  Certified mail with proof of delivery (~$10.50 cost)
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* User Info Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Information
          </h2>
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={userInfo.name}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.name ? "border-red-500" : "border-gray-300"}`}
                placeholder="Jane Doe"
              />
              {errors.name && (
                <p className="text-red-500 text-xs mt-1">{errors.name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={userInfo.email}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.email ? "border-red-500" : "border-gray-300"}`}
                placeholder="jane@example.com"
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Street Address
              </label>
              <input
                type="text"
                name="addressLine1"
                value={userInfo.addressLine1}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.addressLine1 ? "border-red-500" : "border-gray-300"}`}
                placeholder="123 Market St"
              />
              {errors.addressLine1 && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.addressLine1}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Line 2 (Optional)
              </label>
              <input
                type="text"
                name="addressLine2"
                value={userInfo.addressLine2}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900"
                placeholder="Apt 4B"
              />
            </div>

            <div className="grid grid-cols-6 gap-4">
              <div className="col-span-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City
                </label>
                <input
                  type="text"
                  name="city"
                  value={userInfo.city}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.city ? "border-red-500" : "border-gray-300"}`}
                  placeholder="San Francisco"
                />
                {errors.city && (
                  <p className="text-red-500 text-xs mt-1">{errors.city}</p>
                )}
              </div>
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  State
                </label>
                <input
                  type="text"
                  name="state"
                  value={userInfo.state}
                  onChange={(e) =>
                    handleInputChange({
                      ...e,
                      target: {
                        ...e.target,
                        value: e.target.value.toUpperCase().slice(0, 2),
                      },
                    } as any)
                  }
                  className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.state ? "border-red-500" : "border-gray-300"}`}
                  placeholder="CA"
                  maxLength={2}
                />
                {errors.state && (
                  <p className="text-red-500 text-xs mt-1">{errors.state}</p>
                )}
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ZIP
                </label>
                <input
                  type="text"
                  name="zip"
                  value={userInfo.zip}
                  onChange={(e) =>
                    handleInputChange({
                      ...e,
                      target: {
                        ...e.target,
                        value: e.target.value.replace(/\D/g, "").slice(0, 5),
                      },
                    } as any)
                  }
                  className={`w-full px-4 py-2 border rounded-lg text-gray-900 ${errors.zip ? "border-red-500" : "border-gray-300"}`}
                  placeholder="94103"
                  maxLength={5}
                />
                {errors.zip && (
                  <p className="text-red-500 text-xs mt-1">{errors.zip}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Payment Button */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <button
            onClick={handleCheckout}
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-6 rounded-lg text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading
              ? "Processing..."
              : `Pay $${currentPrice.amount.toFixed(2)}`}
          </button>
          <p className="text-sm text-gray-500 text-center mt-4">
            Secure payment powered by Stripe
          </p>
        </div>

        {/* UPL Notice */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
          <p className="text-sm text-gray-700">
            <strong>Final Notice:</strong> By proceeding, you confirm that you
            have reviewed your appeal letter and understand that we do not
            provide legal advice or guarantee outcomes.
          </p>
        </div>

        {/* Back Link */}
        <Link
          href="/appeal/signature"
          className="block text-center text-indigo-600 hover:text-indigo-700 font-medium"
        >
          ← Back to Signature
        </Link>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CheckoutPageContent />
    </Suspense>
  );
}
