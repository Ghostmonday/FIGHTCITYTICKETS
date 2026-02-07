"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

export default function SignaturePage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [signature, setSignature] = useState(state.signature || "");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);

  // Initialize canvas with proper sizing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size for high DPI displays
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Set drawing style
    ctx.strokeStyle = "#111827";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
  }, []);

  const getCanvasCoordinates = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    let clientX: number;
    let clientY: number;

    if ("touches" in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = e.clientX;
      clientY = e.clientY;
    }

    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  };

  const startDrawing = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    e.preventDefault();
    setIsDrawing(true);
    setHasSignature(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const coords = getCanvasCoordinates(e);
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
  };

  const draw = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    if (!isDrawing) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const coords = getCanvasCoordinates(e);
    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dataURL = canvas.toDataURL("image/png");
    setSignature(dataURL);
    updateState({ signature: dataURL });
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    setSignature("");
    setHasSignature(false);
    updateState({ signature: null });
  };

  const handleContinue = () => {
    if (signature) {
      router.push("/appeal/checkout");
    }
  };

  return (
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-heading-lg text-text-primary mb-2">
            Sign Your Appeal
          </h1>
          <p className="text-body text-text-secondary">
            Your signature is required on the official appeal document.
          </p>
        </div>

        <div className="space-y-6">
          {/* Signature Canvas */}
          <Card padding="lg">
            <h2 className="text-heading-md text-text-primary mb-4">
              Draw Your Signature
            </h2>
            <p className="text-body-sm text-text-secondary mb-4">
              Sign using your mouse or finger on a touch screen.
            </p>

            <div className="relative">
              <canvas
                ref={canvasRef}
                className="w-full border-2 border-border rounded-input bg-bg-surface cursor-crosshair touch-none"
                style={{ height: "180px" }}
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                onTouchStart={startDrawing}
                onTouchMove={draw}
                onTouchEnd={stopDrawing}
              />
              {!hasSignature && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <p className="text-text-muted text-body">Sign here</p>
                </div>
              )}
            </div>

            <div className="flex justify-between items-center mt-4">
              <button
                onClick={clearSignature}
                className="text-body text-text-secondary hover:text-text-primary transition-colors"
              >
                Clear signature
              </button>
              {signature && (
                <div className="flex items-center gap-2 text-success">
                  <svg
                    className="w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-body-sm font-medium">
                    Signature captured
                  </span>
                </div>
              )}
            </div>
          </Card>

          {/* Preview */}
          {signature && (
            <Card padding="md">
              <h3 className="text-heading-sm text-text-primary mb-3">
                Signature Preview
              </h3>
              <img
                src={signature}
                alt="Your signature"
                className="max-h-16 border border-border rounded bg-bg-surface p-2"
              />
            </Card>
          )}

          {/* Actions */}
          <div className="flex justify-between items-center pt-4">
            <Link
              href="/appeal/review"
              className="text-body text-text-secondary hover:text-text-primary transition-colors"
            >
              ← Back
            </Link>
            <Button onClick={handleContinue} disabled={!signature}>
              Continue to Payment →
            </Button>
          </div>

          {/* Legal Disclaimer */}
          <LegalDisclaimer variant="compact" className="mt-6" />
        </div>
      </div>
    </main>
  );
}
