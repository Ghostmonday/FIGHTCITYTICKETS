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
  title: "Procedural Compliance Service | What We Are",
  description:
    "We aren't lawyers. We're paperwork experts. Learn about our procedural compliance service for parking ticket appeals.",
};

export default function WhatWeArePage() {
  return (
    <div className="min-h-screen bg-stone-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link
            href="/"
            className="text-stone-600 hover:text-stone-800 font-medium transition-colors"
          >
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg border border-stone-200 p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-light text-stone-800 mb-6 tracking-tight">
            WE AREN&apos;T LAWYERS.
            <br />
            <span className="font-semibold">WE&apos;RE PAPERWORK EXPERTS.</span>
          </h1>

          <p className="text-xl text-stone-600 mb-12 font-light leading-relaxed">
            And in a bureaucracy,{" "}
            <strong className="text-stone-800">paperwork is power</strong>.
          </p>

          {/* PROCEDURAL COMPLIANCE SERVICE */}
          <div className="mb-12">
            <h2 className="text-xl font-semibold text-stone-800 mb-6 border-b border-stone-200 pb-2">
              PROCEDURAL COMPLIANCE SERVICE
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  The Clerical Engine™
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  Our proprietary technology scans your citation for procedural
                  defects—missing elements, misclassification, timing errors, or
                  clerical flaws. We ensure your submission meets the exacting
                  municipal specifications that determine whether an appeal is
                  accepted or rejected.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  Document Preparation
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We take what you tell us—the facts, the circumstances, your
                  side of the story—and format it into a professional appeal
                  letter. We act as a scribe, helping you express what{" "}
                  <strong className="text-stone-800">you</strong> tell us is
                  your reason for appealing.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  Submission Dispatch
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We print and mail your appeal letter via certified or standard
                  mail, ensuring it reaches the proper department within your
                  appeal deadline. We track delivery and provide confirmation.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  Voice Articulation
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We refine and articulate your words into professional,
                  polished language—while preserving your exact factual content,
                  story, and position. Your voice, elevated to meet bureaucratic
                  standards.
                </p>
              </div>
            </div>
          </div>

          {/* WHAT WE ARE NOT */}
          <div className="mb-12">
            <h2 className="text-xl font-semibold text-stone-800 mb-6 border-b border-stone-200 pb-2">
              WHAT WE ARE NOT
            </h2>

            <div className="space-y-6">
              <div className="bg-stone-50 border border-stone-200 p-5 rounded-lg">
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  We Are Not a Law Firm
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We do not employ attorneys. We do not provide legal
                  representation. We do not create attorney-client
                  relationships. We do not practice law.
                </p>
              </div>

              <div className="bg-stone-50 border border-stone-200 p-5 rounded-lg">
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  We Do Not Provide Legal Advice
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We do not interpret laws, regulations, or case law. We do not
                  suggest legal strategies or evaluate the legal merits of your
                  case. We do not tell you what arguments to make.
                </p>
              </div>

              <div className="bg-stone-50 border border-stone-200 p-5 rounded-lg">
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  We Do Not Guarantee Outcomes
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  The decision to dismiss a parking ticket rests entirely with
                  the issuing agency or an administrative judge. We cannot and
                  do not promise that your appeal will be successful.
                </p>
              </div>

              <div className="bg-stone-50 border border-stone-200 p-5 rounded-lg">
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  We Do Not Create Your Content
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We do not invent arguments, suggest evidence, or create legal
                  theories. The factual content, story, and position you provide
                  are entirely yours. We only refine how you express them.
                </p>
              </div>

              <div className="bg-stone-50 border border-stone-200 p-5 rounded-lg">
                <h3 className="text-lg font-medium text-stone-800 mb-2">
                  We Do Not Predict Results
                </h3>
                <p className="text-stone-600 leading-relaxed">
                  We do not tell you whether your appeal will succeed or fail.
                  We do not assess the strength of your case. We do not
                  recommend whether you should appeal.
                </p>
              </div>
            </div>
          </div>

          {/* IMPORTANT DISTINCTION */}
          <div className="bg-stone-100 border border-stone-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-stone-800 mb-4">
              THE IMPORTANT DISTINCTION
            </h2>
            <div className="space-y-4 text-stone-700 leading-relaxed">
              <p>
                A parking ticket appeal is a procedural process, not a legal
                trial. The same requirements that municipalities use to reject
                citizen appeals—missing forms, wrong formatting, missed
                deadlines—can be used to challenge their citations.
              </p>
              <p>
                We help you meet those requirements with precision. That is not
                legal advice—it is administrative compliance. We ensure your
                paperwork is perfect. We do not tell you what to argue.
              </p>
              <p className="font-medium text-stone-800">
                If you require legal representation or legal advice, please
                consult with a licensed attorney in your jurisdiction.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="bg-stone-800 rounded-lg p-6 text-white text-center">
            <h3 className="text-xl font-medium mb-2">
              Ready to Begin Your Submission?
            </h3>
            <p className="text-stone-300 mb-4">
              The Clerical Engine™ awaits your citation.
            </p>
            <Link
              href="/"
              className="inline-block bg-white text-stone-800 px-6 py-3 rounded-lg font-medium hover:bg-stone-100 transition"
            >
              Begin Submission →
            </Link>
          </div>

          <div className="mt-8">
            <LegalDisclaimer variant="full" />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-stone-500">
          <p>© 2025 FightCityTickets.com | Neural Draft LLC</p>
          <p className="mt-1">
            Procedural Compliance. Document Preparation. Clerical Engine™.
          </p>
        </div>
      </div>
    </div>
  );
}
