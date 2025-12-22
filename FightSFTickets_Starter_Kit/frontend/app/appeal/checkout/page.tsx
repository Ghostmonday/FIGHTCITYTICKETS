"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function CheckoutPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";

  const [isLoading, setIsLoading] = useState(false);
  const [checkoutUrl, setCheckoutUrl] = useState<string | null>(null);

  const prices = {
    standard: { amount: 9.0, label: "Standard Mail" },
    certified: { amount: 19.0, label: "Certified Mail" },
  };

  const currentPrice = prices[appealType as keyof typeof prices] || prices.standard;

  const handleCheckout = async () => {
    setIsLoading(true);
    try {
      const { createCheckoutSession } = await import("../../lib/api");
      
      // TODO: Get form data from context/state
      const checkoutData = {
        citation_number: "912345678", // TODO: Get from context
        appeal_type: appealType as "standard" | "certified",
        user_name: "John Doe", // TODO: Get from context
        user_address_line1: "123 Main St", // TODO: Get from context
        user_city: "San Francisco", // TODO: Get from context
        user_state: "CA", // TODO: Get from context
        user_zip: "94102", // TODO: Get from context
        violation_date: "2024-01-15", // TODO: Get from context
        vehicle_info: "Honda Civic", // TODO: Get from context
        appeal_reason: "Sample reason", // TODO: Get from context
        draft_text: "Sample draft text", // TODO: Get from context
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
          : "Failed to start checkout. Please try again."
      );
      setIsLoading(false);
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
              <span className="text-indigo-600">${currentPrice.amount.toFixed(2)}</span>
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

        {/* Payment Button */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <button
            onClick={handleCheckout}
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-6 rounded-lg text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Processing..." : `Pay $${currentPrice.amount.toFixed(2)}`}
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

