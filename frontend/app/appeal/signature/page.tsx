"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

export default function SignaturePage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [signature, setSignature] = useState(state.signature || "");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    const rect = canvas.getBoundingClientRect();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dataURL = canvas.toDataURL();
    setSignature(dataURL);
    updateState({ signature: dataURL });
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setSignature("");
    updateState({ signature: null });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold mb-4">Sign Your Appeal</h1>
          <p className="text-gray-600 mb-6">
            Draw your signature below. This will be included on your appeal
            letter.
          </p>
          <LegalDisclaimer variant="inline" className="mb-4" />

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 mb-4 bg-white">
            <canvas
              ref={canvasRef}
              width={600}
              height={200}
              className="w-full border rounded cursor-crosshair"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
            />
          </div>

          <div className="flex gap-4 mb-6">
            <button
              onClick={clearSignature}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Clear
            </button>
          </div>

          {signature && (
            <div className="mb-6">
              <img
                src={signature}
                alt="Signature preview"
                className="max-w-xs border rounded"
              />
            </div>
          )}

          <div className="flex justify-between">
            <Link
              href="/appeal/review"
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back
            </Link>
            <button
              onClick={() => router.push("/appeal/checkout")}
              disabled={!signature}
              className={`px-6 py-2 rounded-lg ${
                signature
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              Continue to Payment →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
