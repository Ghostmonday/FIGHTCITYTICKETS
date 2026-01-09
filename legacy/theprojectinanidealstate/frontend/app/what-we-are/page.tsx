import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

/**
 * What We Are / What We Are Not Page for FightCityTickets.com
 *
 * Critical compliance page that clearly distinguishes procedural compliance
 * from legal services. Required for UPL compliance and user expectations.
 *
 * Brand Positioning: "We aren't lawyers. We're paperwork experts."
 */

export const metadata = {
  title: "What We Are / What We Are Not | FightCityTickets.com",
  description: "We aren't lawyers. We're paperwork experts. Learn about our procedural compliance service for parking ticket appeals.",
};

export default function WhatWeArePage() {
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
            WE AREN'T LAWYERS. WE'RE PAPERWORK EXPERTS.
          </h1>

          <p className="text-xl text-gray-700 mb-8 font-medium">
            And in a bureaucracy, paperwork is power.
          </p>

          {/* WHAT WE ARE */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-green-500 pb-2">
              WHAT WE ARE
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Procedural Compliance Service
                </h3>
                <p className="text-gray-700">
                  We help you navigate the complex procedural requirements of municipal appeal
                  systems. Think of us as the difference between representing yourself in court
                  (pro se) and having someone help you fill out the forms correctly.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Document Preparation Service
                </h3>
                <p className="text-gray-700">
                  We take what you tell us—the facts, the circumstances, your side of the story—
                  and we format it into a professional appeal letter that meets the exacting
                  standards of the issuing agency.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Submission Service
                </h3>
                <p className="text-gray-700">
                  We print and mail your appeal letter via certified or standard mail, ensuring
                  it reaches the proper department within your appeal deadline.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  The Clerical Engine™
                </h3>
                <p className="text-gray-700">
                  Our technology scans your citation for procedural defects—missing elements,
                  misclassification, timing errors, or clerical flaws that can invalidate an
                  otherwise valid citation. We ensure your submission meets municipal specifications.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Voice Articulation Specialists
                </h3>
                <p className="text-gray-700">
                  We refine and articulate your words into professional, polished language—while
                  preserving your exact factual content, story, and position. We make your voice
                  sound exceptional without changing what you say.
                </p>
              </div>
            </div>
          </div>

          {/* WHAT WE ARE NOT */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-red-500 pb-2">
              WHAT WE ARE NOT
            </h2>

            <div className="space-y-6">
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Are Not a Law Firm
                </h3>
                <p className="text-gray-700">
                  We do not employ attorneys. We do not provide legal representation. We do not
                  create attorney-client relationships. We do not practice law.
                </p>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Provide Legal Advice
                </h3>
                <p className="text-gray-700">
                  We do not interpret laws, regulations, or case law. We do not suggest legal
                  strategies or evaluate the legal merits of your case. We do not tell you
                  what arguments to make.
                </p>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Guarantee Outcomes
                </h3>
                <p className="text-gray-700">
                  The decision to dismiss a parking ticket rests entirely with the issuing agency
                  or an administrative judge. We cannot and do not promise that your appeal will
                  be successful.
                </p>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Create Your Content
                </h3>
                <p className="text-gray-700">
                  We do not invent arguments, suggest evidence, or create legal theories. The
                  factual content, story, and position you provide are entirely yours. We only
                  refine how you express them.
                </p>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Predict Results
                </h3>
                <p className="text-gray-700">
                  We do not tell you whether your appeal will succeed or fail. We do not assess
                  the strength of your case. We do not recommend whether you should appeal.
                </p>
              </div>
            </div>
          </div>

          {/* IMPORTANT DISTINCTION */}
          <div className="bg-gray-100 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              THE IMPORTANT DISTINCTION
            </h2>
            <p className="text-gray-700 mb-4">
              A parking ticket appeal is a procedural process, not a legal trial. The same
              requirements that municipalities use to reject citizen appeals (missing forms,
              wrong formatting, missed deadlines) can be used to challenge their citations.
            </p>
            <p className="text-gray-700 mb-4">
              We help you meet those requirements with precision. That is not legal advice—it
              is administrative compliance. We ensure your paperwork is perfect. We do not tell
              you what to argue.
            </p>
            <p className="text-gray-700 mt-4 font-medium">
              If you need legal representation or legal advice, please consult with a licensed
              attorney in your jurisdiction.
            </p>
          </div>

          {/* CTA */}
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-6 text-white text-center">
            <h3 className="text-xl font-bold mb-2">
              Ready to Submit Your Appeal?
            </h3>
            <p className="text-green-100 mb-4">
              We'll help you submit a procedurally perfect appeal.
            </p>
            <Link
              href="/"
              className="inline-block bg-white text-green-600 px-6 py-3 rounded-lg font-bold hover:bg-green-50 transition"
            >
              Get Started →
            </Link>
          </div>

          <div className="mt-8">
            <LegalDisclaimer variant="full" />
          </div>
        </div>
      </div>
    </div>
  );
}
