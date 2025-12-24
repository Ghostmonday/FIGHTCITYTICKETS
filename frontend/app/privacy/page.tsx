import Link from "next/link";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            Privacy Policy
          </h1>

          <div className="prose prose-indigo max-w-none text-gray-700">
            <p className="lead">
              At FightSFTickets.com, we take your privacy seriously. This Privacy Policy describes how we collect, use, and share your personal information when you use our services.
            </p>

            <h2>1. Information We Collect</h2>
            <p>
              We collect information necessary to prepare and mail your parking ticket appeal, including:
            </p>
            <ul>
              <li><strong>Personal Information:</strong> Name, email address, mailing address, and phone number.</li>
              <li><strong>Citation Information:</strong> Citation number, violation date, vehicle information (make, model, license plate), and violation details.</li>
              <li><strong>Evidence:</strong> Photos, audio recordings, and written statements you provide.</li>
              <li><strong>Payment Information:</strong> We use Stripe to process payments. We do not store your full credit card information on our servers.</li>
            </ul>

            <h2>2. How We Use Your Information</h2>
            <p>
              We use your information to:
            </p>
            <ul>
              <li>Generate your appeal letter.</li>
              <li>Process your payment.</li>
              <li>Mail your appeal to the appropriate agency (e.g., SFMTA) via third-party mail providers.</li>
              <li>Communicate with you about the status of your order.</li>
              <li>Improve our AI models and services (data is anonymized where possible).</li>
            </ul>

            <h2>3. Information Sharing</h2>
            <p>
              We do not sell your personal information. We share your information only with:
            </p>
            <ul>
              <li><strong>Service Providers:</strong> Third-party vendors who help us provide the Service, such as:
                <ul>
                  <li><strong>Stripe:</strong> Payment processing.</li>
                  <li><strong>Lob / Mail Providers:</strong> Printing and mailing services.</li>
                  <li><strong>AI Providers (e.g., OpenAI, DeepSeek):</strong> Generating appeal text (processed securely).</li>
                  <li><strong>Cloud Hosting:</strong> Hosting our infrastructure.</li>
                </ul>
              </li>
              <li><strong>Legal Requirements:</strong> If required by law, subpoena, or legal process.</li>
            </ul>

            <h2>4. Data Security</h2>
            <p>
              We implement industry-standard security measures to protect your information, including encryption in transit and at rest. However, no method of transmission over the Internet is 100% secure.
            </p>

            <h2>5. Your Rights (CCPA/GDPR)</h2>
            <p>
              Depending on your location, you may have the right to:
            </p>
            <ul>
              <li>Access the personal information we hold about you.</li>
              <li>Request correction of inaccurate information.</li>
              <li>Request deletion of your personal information ("Right to be Forgotten").</li>
              <li>Opt-out of certain data processing.</li>
            </ul>
            <p>
              To exercise these rights, please contact us at support@fightsftickets.com.
            </p>

            <h2>6. Cookies</h2>
            <p>
              We use cookies to improve your experience, such as keeping you logged in or remembering your preferences. You can control cookies through your browser settings.
            </p>

            <h2>7. Children's Privacy</h2>
            <p>
              Our Service is not intended for children under 13. We do not knowingly collect personal information from children under 13.
            </p>

            <h2>8. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.
            </p>

            <h2>9. Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy, please contact us at support@fightsftickets.com.
            </p>

            <p className="text-sm text-gray-500 mt-8">
              Last Updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
