import Link from "next/link";

/**
 * Contact / Support Page for FIGHTCITYTICKETS.com
 *
 * Required for platform legitimacy and user trust.
 * Provides visible accountability for the business.
 *
 * Brand Positioning: "We aren't lawyers. We're paperwork experts."
 */

export const metadata = {
  title: "Contact Us | FIGHTCITYTICKETS.com",
  description:
    "Contact FIGHTCITYTICKETS.com - We're here to help with your parking ticket appeal",
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link
            href="/"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Contact Us
          </h1>

          <p className="text-xl text-gray-600 mb-8">
            We&apos;re here to help with your parking ticket appeal.
          </p>

          {/* Contact Methods */}
          <div className="grid md:grid-cols-2 gap-6 mb-10">
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center mb-4">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Email Support
              </h2>
              <p className="text-gray-600 mb-4">
                Best for: General questions, appeal status, technical issues
              </p>
              <a
                href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}
              </a>
              <p className="text-sm text-gray-500 mt-2">
                Response within 24-48 hours
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <div className="w-12 h-12 bg-green-600 text-white rounded-lg flex items-center justify-center mb-4">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Appeal Status
              </h2>
              <p className="text-gray-600 mb-4">
                Check the status of your appeal online
              </p>
              <Link
                href="/appeal/status"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Check Status →
              </Link>
              <p className="text-sm text-gray-500 mt-2">Available 24/7</p>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Common Questions
            </h2>

            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  How long does the process take?
                </h3>
                <p className="text-gray-600">
                  Your appeal letter is mailed within 1-2 business days after
                  payment. The city typically responds within 2-4 weeks.
                </p>
              </div>

              <div className="border-b border-gray-200 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  What happens after I submit?
                </h3>
                <p className="text-gray-600">
                  We mail your appeal to the city. You&apos;ll receive a
                  tracking number to confirm delivery. The city will respond
                  directly to you by mail with their decision.
                </p>
              </div>

              <div className="border-b border-gray-200 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Do you guarantee my ticket will be dismissed?
                </h3>
                <p className="text-gray-600">
                  <strong>We do not guarantee outcomes.</strong> The decision
                  rests entirely with the issuing agency. We ensure your appeal
                  is professionally formatted and submitted
                  correctly—that&apos;s our service.
                </p>
              </div>

              <div className="border-b border-gray-200 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  What is your refund policy?
                </h3>
                <p className="text-gray-600">
                  Full refund if you cancel before mailing. No refunds after
                  mailing or if the appeal outcome is unfavorable. See our{" "}
                  <Link
                    href="/refund"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    Refund Policy
                  </Link>{" "}
                  for details.
                </p>
              </div>

              <div className="border-b border-gray-200 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">
                  Are you a law firm?
                </h3>
                <p className="text-gray-600">
                  <strong>
                    No, we aren&apos;t lawyers. We&apos;re paperwork experts.
                  </strong>{" "}
                  We are a document preparation service that helps you format
                  and submit your own appeal. We do not provide legal advice or
                  representation.
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  What cities do you support?
                </h3>
                <p className="text-gray-600">
                  We support parking ticket appeals in 15+ cities including San
                  Francisco, Los Angeles, New York City, Chicago, Seattle,
                  Denver, Portland, Philadelphia, Houston, Dallas, and more.
                </p>
              </div>
            </div>
          </div>

          {/* Business Information */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Business Information
            </h2>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">
                  <strong>Service:</strong> Document Preparation & Mailing
                </p>
                <p className="text-gray-600 mt-1">
                  <strong>Jurisdiction:</strong> United States
                </p>
              </div>
              <div>
                <p className="text-gray-600">
                  <strong>Payment Processor:</strong> Stripe
                </p>
                <p className="text-gray-600 mt-1">
                  <strong>Mailing Partner:</strong> Lob (USPS)
                </p>
              </div>
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 text-sm">
              <strong>Legal Notice:</strong> We are not a law firm and do not
              provide legal advice. If you need legal representation, please
              consult with a licensed attorney in your jurisdiction. Our service
              helps you prepare and submit your own appeal documents—we do not
              advocate for you in legal matters.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
