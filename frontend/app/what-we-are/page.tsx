import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

export const metadata = {
  title: "What We Are / What We Are Not | FIGHTCITYTICKETS.com",
  description: "We aren't lawyers. We're paperwork experts. Learn about our procedural compliance service for parking ticket appeals.",
};

export default function WhatWeArePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link href="/" className="text-stone-600 hover:text-stone-800 font-medium">
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            WE AREN&apos;T LAWYERS. WE&apos;RE PAPERWORK EXPERTS.
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
                  otherwise valid citation.
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
                  create attorney-client relationships.
                </p>
              </div>

              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Provide Legal Advice
                </h3>
                <p className="text-gray-700">
                  We do not interpret laws, regulations, or case law. We do not suggest legal
                  strategies or evaluate the legal merits of your case.
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
                  We Do Not Practice Law
                </h3>
                <p className="text-gray-700">
                  We operate strictly within the bounds of document preparation services. We help
                  you express YOUR position—we do not tell you what position to take.
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
            <p className="text-gray-700">
              We help you meet those requirements with precision. That is not legal advice—it
              is administrative compliance.
            </p>
            <p className="text-gray-700 mt-4 font-medium">
              If you need legal representation or legal advice, please consult with a licensed
              attorney in your jurisdiction.
            </p>
          </div>

          <LegalDisclaimer variant="full" />
        </div>
      </div>
    </div>
  );
}
