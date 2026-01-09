import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

/**
 * Refund Policy Page for FightCityTickets.com
 *
 * Required for payment processor compliance.
 * Clearly defines refund terms to prevent chargebacks and disputes.
 *
 * Brand Positioning: "We aren't lawyers. We're paperwork experts."
 */

export const metadata = {
  title: "Refund Policy | FightCityTickets.com",
  description:
    "Refund policy for FightCityTickets.com - Procedural compliance service for parking ticket appeals",
};

export default function RefundPage() {
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
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            Refund Policy
          </h1>

          <div className="prose prose-indigo max-w-none text-gray-700">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
              <p className="text-blue-800">
                <strong>Important:</strong> We are a document preparation and
                mailing service. We do not guarantee appeal outcomes. Refunds
                are based on service delivery, not case results.
              </p>
            </div>

            <h2>1. Overview</h2>
            <p>
              At FightCityTickets.com, we understand that circumstances can
              change. This refund policy is designed to be fair and transparent
              while protecting both you and our business.
            </p>
            <p>
              <strong>We aren't lawyers. We're paperwork experts.</strong> Our
              service is to prepare and mail your appeal exactly as you provide
              it. We do not control the outcome of your appeal—that rests with
              the municipal agency.
            </p>

            <h2>2. When Refunds Are Available</h2>

            <div className="space-y-4">
              <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
                <h3 className="font-bold text-green-900 mb-2">
                  ✅ Full Refund Available
                </h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>
                    <strong>Before mailing:</strong> If you cancel before your
                    appeal has been printed or mailed, you may request a full
                    refund.
                  </li>
                  <li>
                    <strong>Processing error:</strong> If we make an error in
                    processing your appeal, you'll receive a full refund plus a
                    credit toward future use.
                  </li>
                  <li>
                    <strong>Service unavailable:</strong> If we're unable to
                    provide the service for any reason, you'll receive a full
                    refund.
                  </li>
                  <li>
                    <strong>Duplicate payment:</strong> If you're charged
                    multiple times for the same appeal.
                  </li>
                </ul>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
                <h3 className="font-bold text-yellow-900 mb-2">
                  ⚠️ Partial Refund Available
                </h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>
                    <strong>After mailing:</strong> Once your appeal has been
                    mailed, we can only offer a partial refund (mailing costs
                    are non-refundable).
                  </li>
                  <li>
                    <strong>Deadline passed:</strong> If the appeal deadline has
                    passed and we couldn't mail in time, partial refund (minus
                    processing fees).
                  </li>
                </ul>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                <h3 className="font-bold text-red-900 mb-2">
                  ❌ No Refund Available
                </h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>
                    <strong>Appeal outcome:</strong> We do not guarantee appeal
                    success. Refunds are not based on whether your appeal is
                    granted or denied.
                  </li>
                  <li>
                    <strong>User error:</strong> If you provided incorrect
                    information that prevented mailing (wrong address, invalid
                    citation number).
                  </li>
                  <li>
                    <strong>Change of mind after mailing:</strong> Once the
                    appeal is mailed, the service is considered rendered.
                  </li>
                  <li>
                    <strong>City processing time:</strong> Delays in city
                    response are beyond our control.
                  </li>
                </ul>
              </div>
            </div>

            <h2>3. How to Request a Refund</h2>
            <p>To request a refund, please contact us at:</p>
            <div className="bg-gray-50 rounded-lg p-4 my-4">
              <p className="text-gray-700">
                <strong>Email:</strong> refunds@fightcitytickets.com
              </p>
              <p className="text-gray-700 mt-2">Please include:</p>
              <ul className="list-disc list-inside text-gray-700 mt-1">
                <li>Your email address</li>
                <li>Your citation number</li>
                <li>Reason for refund request</li>
                <li>Order date (if known)</li>
              </ul>
            </div>

            <h2>4. Refund Processing Timeline</h2>
            <ul>
              <li>
                <strong>Initial response:</strong> Within 2 business days
              </li>
              <li>
                <strong>Refund approval:</strong> Within 5 business days of
                request
              </li>
              <li>
                <strong>Credit to account:</strong> 5-10 business days
              </li>
              <li>
                <strong>Credit card refund:</strong> 10-15 business days
                (depends on your bank)
              </li>
            </ul>

            <h2>5. Chargebacks and Disputes</h2>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 my-4">
              <p className="text-yellow-900 font-medium">
                Important: If you dispute a charge with your bank or credit card
                company without first contacting us, we may suspend your account
                pending resolution.
              </p>
            </div>
            <p>
              We encourage you to contact us directly if you have concerns about
              a charge. Most issues can be resolved quickly through direct
              communication.
            </p>

            <h2>6. Service Description</h2>
            <p>Our service includes:</p>
            <ul>
              <li>
                Formatting your appeal letter according to municipal
                requirements
              </li>
              <li>
                Printing and mailing your appeal to the appropriate agency
              </li>
              <li>Providing tracking information when available</li>
              <li>Customer support during the process</li>
            </ul>
            <p>
              Our service does <strong>not</strong> include:
            </p>
            <ul>
              <li>Legal advice or representation</li>
              <li>Guaranteed appeal outcomes</li>
              <li>Communication with the city on your behalf</li>
              <li>Advice on whether you should appeal</li>
            </ul>

            <h2>7. Contact Us</h2>
            <p>
              If you have questions about this refund policy or need to request
              a refund:
            </p>
            <div className="bg-gray-50 rounded-lg p-4 mt-4">
              <p className="text-gray-700">
                <strong>Email:</strong> refunds@fightcitytickets.com
              </p>
              <p className="text-gray-700 mt-2">
                <strong>Response time:</strong> We respond to all refund
                requests within 2 business days.
              </p>
            </div>

            <div className="mt-8">
              <LegalDisclaimer variant="full" />
            </div>
          </div>

          <div className="mt-8 text-center">
            <Link
              href="/"
              className="inline-block bg-green-600 text-white px-8 py-4 rounded-lg font-bold hover:bg-green-700 transition"
            >
              Return to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
