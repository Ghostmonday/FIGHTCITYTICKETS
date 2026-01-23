import Link from "next/link";

/**
 * Privacy Policy Page for FIGHTCITYTICKETS.com
 *
 * Critical operational compliance page required for:
 * - Payment processor requirements (Stripe)
 * - Hosting provider requirements
 * - Regulatory visibility
 * - User trust
 *
 * Brand Positioning: "We aren't lawyers. We're paperwork experts."
 */

export const metadata = {
  title: "Privacy Policy | FIGHTCITYTICKETS.com",
  description:
    "Privacy policy for FIGHTCITYTICKETS.com - Procedural compliance service for parking ticket appeals",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link
            href="/"
            className="text-stone-600 hover:text-stone-800 font-medium"
          >
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            Privacy Policy
          </h1>

          <div className="prose prose-stone max-w-none text-gray-700">
            <p className="lead text-lg text-gray-600 mb-8">
              <strong>
                We aren&apos;t lawyers. We&apos;re paperwork experts.
              </strong>{" "}
              And in a bureaucracy, paperwork is power. We respect your privacy.
              This policy explains how we handle your data.
            </p>

            <div className="bg-stone-50 border border-stone-200 rounded-lg p-4 mb-8">
              <p className="text-sm text-stone-800">
                <strong>Important:</strong> We are a procedural compliance
                service, not a law firm. We do not sell, share, or monetize your
                personal data. Your information is used only to process and
                submit your appeal as you direct.
              </p>
            </div>

            <h2>1. Information We Collect</h2>
            <p>
              We collect only the information necessary to process your appeal:
            </p>

            <div className="grid md:grid-cols-2 gap-6 my-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">
                  Personal Information
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  <li>Full name</li>
                  <li>Email address</li>
                  <li>Physical mailing address</li>
                  <li>Phone number (optional)</li>
                </ul>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">
                  Citation Information
                </h3>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  <li>Citation number</li>
                  <li>Violation date and location</li>
                  <li>Vehicle information (make, model, license plate)</li>
                  <li>Violation details</li>
                </ul>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">
                Evidence You Provide
              </h3>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li>Photos of parking signs, meters, or circumstances</li>
                <li>Written statements about your situation</li>
                <li>Voice recordings (if you use voice input)</li>
                <li>Digital signature</li>
              </ul>
            </div>

            <h2>2. How We Use Your Information</h2>
            <p>Your information is used only for these specific purposes:</p>
            <ul>
              <li>
                <strong>The Clerical Engine™:</strong> Formatting your appeal
                letter to meet municipal procedural requirements
              </li>
              <li>
                <strong>Submission:</strong> Mailing your appeal to the
                appropriate city agency
              </li>
              <li>
                <strong>Communication:</strong> Sending you updates about your
                appeal status
              </li>
              <li>
                <strong>Payment Processing:</strong> Processing your payment
                securely via Stripe
              </li>
              <li>
                <strong>Record Keeping:</strong> Maintaining records as required
                by law
              </li>
            </ul>

            <h2>3. Information Sharing</h2>
            <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded mb-4">
              <p className="text-green-900 font-medium">
                We do not sell your personal information. Ever.
              </p>
            </div>
            <p>We share your information only with:</p>
            <ul>
              <li>
                <strong>Service Providers:</strong> Third parties who help us
                operate:
                <ul>
                  <li>Stripe (payment processing)</li>
                  <li>Lob (mailing services)</li>
                  <li>
                    AI services (statement refinement - data is processed
                    securely)
                  </li>
                  <li>Cloud hosting providers</li>
                </ul>
              </li>
              <li>
                <strong>Legal Requirements:</strong> If required by law,
                subpoena, or valid government request
              </li>
              <li>
                <strong>City Agencies:</strong> The municipal authority
                processing your appeal (this is the intended purpose)
              </li>
            </ul>

            <h2>4. Data Retention</h2>
            <p>We retain your information for the following periods:</p>
            <table className="w-full my-4 border-collapse">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3">Data Type</th>
                  <th className="text-left py-2 px-3">Retention Period</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="py-2 px-3">Appeal records</td>
                  <td className="py-2 px-3">3 years (legal requirement)</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2 px-3">Payment records</td>
                  <td className="py-2 px-3">7 years (tax compliance)</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2 px-3">Evidence photos</td>
                  <td className="py-2 px-3">1 year after appeal resolved</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-2 px-3">User account data</td>
                  <td className="py-2 px-3">
                    Until account deletion requested
                  </td>
                </tr>
                <tr>
                  <td className="py-2 px-3">Marketing communications</td>
                  <td className="py-2 px-3">Until unsubscribe</td>
                </tr>
              </tbody>
            </table>

            <h2>5. Your Rights</h2>
            <p>You have the following rights regarding your data:</p>
            <ul>
              <li>
                <strong>Access:</strong> You can request a copy of all data we
                hold about you
              </li>
              <li>
                <strong>Correction:</strong> You can request correction of
                inaccurate information
              </li>
              <li>
                <strong>Deletion:</strong> You can request deletion of your data
                (subject to legal retention requirements)
              </li>
              <li>
                <strong>Export:</strong> You can request your data in a portable
                format
              </li>
              <li>
                <strong>Opt-Out:</strong> You can unsubscribe from marketing
                communications at any time
              </li>
            </ul>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 my-6">
              <p className="text-yellow-900 text-sm">
                <strong>Note:</strong> Some data cannot be deleted due to legal
                retention requirements (payment records, tax compliance). We
                will inform you what can and cannot be deleted when you make a
                request.
              </p>
            </div>

            <h2>6. Data Security</h2>
            <p>We implement industry-standard security measures:</p>
            <ul>
              <li>Encryption in transit (HTTPS/TLS)</li>
              <li>Encryption at rest for sensitive data</li>
              <li>Secure payment processing via Stripe (PCI DSS compliant)</li>
              <li>Access controls and authentication</li>
              <li>Regular security updates and monitoring</li>
            </ul>
            <p className="mt-2 text-sm text-gray-600">
              No method of transmission over the Internet or electronic storage
              is 100% secure. While we use commercially acceptable means to
              protect your data, we cannot guarantee absolute security.
            </p>

            <h2>7. Cookies and Tracking</h2>
            <p>We use cookies for:</p>
            <ul>
              <li>
                <strong>Essential Cookies:</strong> Required for the appeal
                process to function
              </li>
              <li>
                <strong>Session Cookies:</strong> Maintaining your progress
                through the appeal flow
              </li>
              <li>
                <strong>Analytics:</strong> Understanding how users interact
                with our site (anonymized)
              </li>
            </ul>
            <p>You can control cookies through your browser settings.</p>

            <h2>8. Third-Party Services</h2>
            <p>Our service integrates with third-party services:</p>
            <ul>
              <li>
                <strong>Stripe:</strong> Payment processing. Their privacy
                policy applies to payment data.
              </li>
              <li>
                <strong>Lob:</strong> Physical mailing services. They receive
                only what is necessary to mail your appeal.
              </li>
              <li>
                <strong>AI Services:</strong> Statement refinement. Data is
                processed securely and not stored by AI providers.
              </li>
            </ul>

            <h2>9. Children&apos;s Privacy</h2>
            <p>
              Our service is not intended for individuals under 13 years of age.
              We do not knowingly collect personal information from children.
            </p>

            <h2>10. International Users</h2>
            <p>
              Our service is operated from the United States. If you access our
              service from outside the US, you consent to the transfer and
              processing of your information in the United States.
            </p>

            <h2>11. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will
              notify you of any material changes by posting the new Privacy
              Policy on this page and updating the &quot;Last Updated&quot;
              date.
            </p>

            <h2>12. Contact Us</h2>
            <p>For any privacy-related questions or requests:</p>
            <div className="bg-gray-100 rounded-lg p-4 my-4">
              <p className="text-gray-700">
                <strong>Email:</strong> {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "privacy@example.com"}
              </p>
              <p className="text-gray-700">
                <strong>Response Time:</strong> We respond to all inquiries
                within 5 business days.
              </p>
            </div>

            <div className="mt-8 p-4 bg-stone-50 rounded-lg">
              <h3 className="font-semibold text-stone-900 mb-2">
                Important Disclaimer
              </h3>
              <p className="text-sm text-stone-800">
                <strong>
                  We aren&apos;t lawyers. We&apos;re paperwork experts.
                </strong>{" "}
                And in a bureaucracy, paperwork is power. This Privacy Policy
                describes how we handle your data for our procedural compliance
                services. We do not provide legal advice. For legal matters,
                please consult with a licensed attorney.
              </p>
            </div>

            <p className="text-sm text-gray-500 mt-8">
              Last Updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
