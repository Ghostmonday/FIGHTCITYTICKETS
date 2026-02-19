"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

export const dynamic = "force-dynamic";

export default function SignaturePage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [signature, setSignature] = useState(state.signature || "");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    // Use theme-aware color
    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#111827';
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

    return { x: clientX - rect.left, y: clientY - rect.top };
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
    <main className="min-h-[calc(100vh-5rem)] px-4 py-8 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 theme-transition" style={{ color: "var(--text-primary)" }}>
            Sign Your Appeal
          </h1>
          <p className="theme-transition" style={{ color: "var(--text-secondary)" }}>
            Your signature is required on the official appeal document
          </p>
        </div>

        {/* Signature Card */}
        <div className="card-step p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3 theme-transition" style={{ color: "var(--text-primary)" }}>
            Draw Your Signature
          </h2>
          <p className="mb-4" style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            Sign using your mouse or finger
          </p>

          <div className="relative">
            <canvas
              ref={canvasRef}
              className="w-full rounded-input cursor-crosshair touch-none"
              style={{ 
                height: "180px", 
                backgroundColor: "var(--bg-surface)",
                border: "2px solid var(--border)"
              }}
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
                <p style={{ color: "var(--text-muted)" }}>Sign here</p>
              </div>
            )}
          </div>

          <div className="flex justify-between items-center mt-4">
            <button
              onClick={clearSignature}
              className="font-medium"
              style={{ color: "var(--text-secondary)" }}
            >
              Clear
            </button>
            {signature && (
              <div className="flex items-center gap-2" style={{ color: "#10B981" }}>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span style={{ fontSize: "0.875rem" }}>Signature captured</span>
              </div>
            )}
          </div>
        </div>

        {/* Preview */}
        {signature && (
          <div className="card-step p-4 mb-6">
            <h3 className="font-semibold mb-2" style={{ color: "var(--text-primary)" }}>Preview</h3>
            <img 
              src={signature} 
              alt="Your signature" 
              className="max-h-16 rounded p-2"
              style={{ backgroundColor: "var(--bg-surface)" }}
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4 mb-6">
          <Link href="/appeal/review" className="btn-secondary flex-1">
            ← Back
          </Link>
          <button 
            onClick={handleContinue} 
            disabled={!signature}
            className="btn-strike flex-1"
          >
            Continue to Payment →
          </button>
        </div>

        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}
