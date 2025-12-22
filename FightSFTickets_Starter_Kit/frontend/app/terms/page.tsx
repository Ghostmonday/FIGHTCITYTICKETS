import Link from "next/link";

export default function TermsPage() {
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
            Terms of Service
          </h1>

          <div className="prose prose-indigo max-w-none text-gray-700">
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
              <h3 className="text-lg font-bold text-yellow-800 mb-2">
                ⚠️ Legal Disclaimer: Non-Lawyer / Unauthorized Practice of Law (UPL) Notice
              </h3>
              <p className="text-sm text-yellow-800">
                FightSFTickets.com ("Service") is a <strong>document preparation service</strong>. We are <strong>NOT a law firm</strong>, and we are <strong>NOT attorneys</strong>. We do not provide legal advice, legal representation, or legal recommendations.
              </p>
              <p className="text-sm text-yellow-800 mt-2">
                Our AI-powered tools assist you in formatting your own appeal based on the information you provide. You are solely responsible for the content, accuracy, and submission of your appeal. Using this Service does not create an attorney-client relationship. If you have a legal problem, you should consult a licensed attorney.
              </p>
            </div>

            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using FightSFTickets.com, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our Service.
            </p>

            <h2>2. Service Description</h2>
            <p>
              FightSFTickets.com provides automated tools to help users generate and mail parking ticket appeal letters. Our services include:
            </p>
            <ul>
              <li>Formatting user-provided information into a letter.</li>
              <li>Printing and mailing documents via third-party carriers (e.g., USPS).</li>
              <li>Providing tracking information where applicable.</li>
            </ul>
            <p>
              We do <strong>not</strong> guarantee that your appeal will be successful. The outcome of your appeal depends entirely on the decision of the issuing agency (e.g., SFMTA).
            </p>

            <h2>3. User Responsibilities</h2>
            <p>
              You agree to:
            </p>
            <ul>
              <li>Provide accurate, current, and complete information.</li>
              <li>Review the final draft of your appeal letter before submission.</li>
              <li>Ensure your appeal is submitted before any deadlines. We are not responsible for missed deadlines.</li>
            </ul>

            <h2>4. Payments and Refunds</h2>
            <p>
              <strong>Payment:</strong> Payment is required at the time of service selection. We use Stripe for secure payment processing.
            </p>
            <p>
              <strong>Refund Policy:</strong>
            </p>
            <ul>
              <li><strong>Before Mailing:</strong> If you cancel before your letter has been printed or mailed, you may be eligible for a full refund.</li>
              <li><strong>After Mailing:</strong> Once a letter has been processed for printing or mailing, services are considered rendered, and <strong>no refunds</strong> will be issued.</li>
              <li><strong>Outcome-Based:</strong> We do <strong>not</strong> offer refunds based on the outcome of your appeal. You are paying for the document preparation and mailing service, not the result.</li>
            </ul>

            <h2>5. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, FightSFTickets.com and its affiliates shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to lost profits, data loss, or the cost of substitute services, arising out of or in connection with your use of the Service.
            </p>
            <p>
              Our total liability to you for any claim arising out of the Service shall not exceed the amount you paid to us for the specific service giving rise to the claim.
            </p>

            <h2>6. Termination</h2>
            <p>
              We reserve the right to terminate or suspend your access to the Service at our sole discretion, without notice, for conduct that we believe violates these Terms or is harmful to other users, us, or third parties, or for any other reason.
            </p>

            <h2>7. Changes to Terms</h2>
            <p>
              We may modify these Terms at any time. If we make material changes, we will notify you by posting the updated Terms on the website. Your continued use of the Service after such changes constitutes your acceptance of the new Terms.
            </p>

            <h2>8. Contact Us</h2>
            <p>
              If you have any questions about these Terms, please contact us at support@fightsftickets.com.
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
