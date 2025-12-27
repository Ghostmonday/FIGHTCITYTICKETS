import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

export default function RefundPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-6">
            Refund Policy
          </h1>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Our Refund Policy
              </h2>
              <p className="text-gray-700 mb-4">
                At FightCityTickets.com, we understand that circumstances can
                change. Here's our clear and fair refund policy:
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                When Refunds Are Available
              </h2>
              <div className="space-y-4">
                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                  <h3 className="font-bold text-green-900 mb-2">
                    ✅ Full Refund Available
                  </h3>
                  <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
                    <li>
                      <strong>Before mailing:</strong> If your appeal hasn't
                      been mailed yet, you can request a full refund.
                    </li>
                    <li>
                      <strong>Processing error:</strong> If we make an error in
                      processing your appeal, you'll receive a full refund.
                    </li>
                    <li>
                      <strong>Service unavailable:</strong> If we're unable to
                      provide the service for any reason, full refund.
                    </li>
                  </ul>
                </div>

                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                  <h3 className="font-bold text-yellow-900 mb-2">
                    ⚠️ Partial Refund Available
                  </h3>
                  <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
                    <li>
                      <strong>After mailing:</strong> Once your appeal has been
                      mailed, we can only offer a partial refund (minus mailing
                      costs).
                    </li>
                    <li>
                      <strong>Appeal deadline passed:</strong> If the appeal
                      deadline has passed and we couldn't mail in time, partial
                      refund.
                    </li>
                  </ul>
                </div>

                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <h3 className="font-bold text-red-900 mb-2">
                    ❌ No Refund Available
                  </h3>
                  <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
                    <li>
                      <strong>Appeal outcome:</strong> We don't guarantee appeal
                      success. Refunds are not based on appeal outcome.
                    </li>
                    <li>
                      <strong>User error:</strong> If you provided incorrect
                      information that prevented mailing, no refund.
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                How to Request a Refund
              </h2>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <p className="text-gray-700 mb-4">
                  To request a refund, please contact us with:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
                  <li>Your email address</li>
                  <li>Your citation number</li>
                  <li>Reason for refund request</li>
                </ul>
                <a
                  href="mailto:refunds@fightcitytickets.com?subject=Refund Request"
                  className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  Request Refund via Email
                </a>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Refund Processing Time
              </h2>
              <p className="text-gray-700 mb-4">
                Refunds are typically processed within{" "}
                <strong>5-10 business days</strong> of approval. The refund will
                be issued to the original payment method.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Questions?
              </h2>
              <p className="text-gray-700 mb-4">
                If you have questions about our refund policy, please contact
                us:
              </p>
              <div className="bg-gray-50 rounded-lg p-6">
                <p className="text-gray-700">
                  <strong>Email:</strong>{" "}
                  <a
                    href="mailto:support@fightcitytickets.com"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    support@fightcitytickets.com
                  </a>
                </p>
              </div>
            </section>

            <LegalDisclaimer variant="elegant" className="mt-8" />
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
