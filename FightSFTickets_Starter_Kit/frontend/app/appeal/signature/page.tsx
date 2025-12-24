"use client";

import { useState, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "../../lib/appeal-context";

function SignaturePageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";
  const { state, updateState } = useAppeal();

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  // Agency display names
  const agencyDisplayNames: Record<string, string> = {
    SFMTA: "SFMTA (San Francisco Municipal Transportation Agency)",
    SFPD: "San Francisco Police Department",
    SFSU: "San Francisco State University",
    SFMUD: "San Francisco Municipal Utility District",
    UNKNOWN: "San Francisco Parking Citation Agency",
  };
  const [hasSignature, setHasSignature] = useState(false);
  const [attestationChecked, setAttestationChecked] = useState(false);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    setIsDrawing(true);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    setHasSignature(true);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
  };

  const getSignatureData = (): string | null => {
    const canvas = canvasRef.current;
    if (!canvas || !hasSignature) return null;

    return canvas.toDataURL("image/png");
  };

  const handleContinue = () => {
    if (!hasSignature || !attestationChecked) {
      alert("Please provide your signature and confirm the attestation");
      return;
    }

    const signatureData = getSignatureData();
    updateState({ signature: signatureData });
    router.push(`/appeal/checkout?type=${appealType}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/appeal/review"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Sign Your Appeal
          </h1>
          <p className="text-gray-600 mt-2">
            Step 5 of 5: Sign your appeal letter
          </p>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm font-medium text-gray-700">
                  Citation #{state.citationNumber || "Not provided"}
                </p>
                <p className="text-sm text-gray-600">
                  Agency: {agencyDisplayNames[state.agency || "UNKNOWN"]}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">
                  Appeal type:{" "}
                  {appealType === "certified"
                    ? "Certified Mail ($19)"
                    : "Standard Mail ($9)"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Signature Pad */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Draw Your Signature
          </h2>
          <div className="border-2 border-gray-300 rounded-lg p-4 bg-white">
            <canvas
              ref={canvasRef}
              width={600}
              height={200}
              className="border border-gray-200 rounded cursor-crosshair w-full"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
            />
          </div>
          <button
            onClick={clearSignature}
            className="mt-4 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
          >
            Clear Signature
          </button>
        </div>

        {/* Attestation */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={attestationChecked}
              onChange={(e) => setAttestationChecked(e.target.checked)}
              className="mt-1 mr-3 w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <span className="text-sm text-gray-700">
              I attest that the information provided in this appeal is true and
              accurate to the best of my knowledge. I understand that providing
              false information may result in penalties.
            </span>
          </label>
        </div>

        {/* UPL Notice */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
          <p className="text-sm text-gray-700">
            <strong>Important:</strong> By signing, you confirm that you have
            reviewed your appeal letter and are responsible for its contents.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4">
          <Link
            href="/appeal/review"
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium text-center hover:bg-gray-50 transition-colors"
          >
            ← Back
          </Link>
          <button
            onClick={handleContinue}
            disabled={!hasSignature || !attestationChecked}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Payment →
          </button>
        </div>
      </div>
    </div>
  );
}

export default function SignaturePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SignaturePageContent />
    </Suspense>
  );
}
