"use client";

import { useState, useCallback, useRef, type ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import type { AppealState } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { extractTextFromImage } from "../../lib/ocr-helper";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

interface OcrResult {
  citationNumber?: string;
  confidence: number;
  rawText: string;
}

export default function CameraPage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [photos, setPhotos] = useState<string[]>(state.photos || []);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrResults, setOcrResults] = useState<OcrResult[]>([]);
  const [manualCitation, setManualCitation] = useState(state.citationNumber || "");
  const [showManualInput, setShowManualInput] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Start camera for live capture
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
    } catch (error) {
      console.error("Failed to access camera:", error);
      alert("Unable to access camera. Please use file upload instead.");
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  // Capture photo from camera
  const capturePhoto = () => {
    if (!videoRef.current) return;

    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0);
    const base64 = canvas.toDataURL("image/jpeg", 0.8);

    handlePhotoCapture(base64);
  };

  // Process a captured or uploaded photo
  const handlePhotoCapture = async (base64: string) => {
    setIsProcessing(true);
    const newPhotos = [...photos, base64];

    // Run OCR on the image
    let ocrResult: OcrResult = { confidence: 0, rawText: "" };
    try {
      ocrResult = await extractTextFromImage(base64);
    } catch (error) {
      console.warn("OCR failed for image:", error);
    }

    const newOcrResults = [...ocrResults, ocrResult];

    setPhotos(newPhotos);
    setOcrResults(newOcrResults);
    updateState((prev: AppealState) => ({ ...prev, photos: newPhotos }));
    setIsProcessing(false);
  };

  // Handle file upload
  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    setIsProcessing(true);

    for (const file of Array.from(files)) {
      const reader = new FileReader();
      const base64 = await new Promise<string>((resolve, reject) => {
        reader.onload = (event) => {
          resolve(event.target?.result as string);
        };
        reader.onerror = () => reject(new Error("Failed to read file"));
        reader.readAsDataURL(file);
      });
      await handlePhotoCapture(base64);
    }

    setIsProcessing(false);
  };

  const removePhoto = (index: number): void => {
    const newPhotos = photos.filter((_: string, i: number) => i !== index);
    const newOcrResults = ocrResults.filter((_: OcrResult, i: number) => i !== index);
    setPhotos(newPhotos);
    setOcrResults(newOcrResults);
    updateState({ photos: newPhotos });
  };

  const handleManualCitationSubmit = (): void => {
    if (manualCitation.trim()) {
      updateState({ citationNumber: manualCitation.trim().toUpperCase() });
      setShowManualInput(false);
    }
  };

  const useOcrCitation = (index: number): void => {
    const result: OcrResult = ocrResults[index];
    if (result.citationNumber) {
      updateState({ citationNumber: result.citationNumber.toUpperCase() });
      setManualCitation(result.citationNumber);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold mb-4 text-stone-800">
            Submit Evidence
          </h1>
          <p className="text-gray-600 mb-6">
            Upload photos of parking signs, meters, or circumstances that
            support your procedural appeal. The Clerical Engine will attach
            these to your submission.
          </p>

          {/* Telemetry opt-in */}
          <div className="bg-stone-50 border border-stone-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="telemetry-optin"
                className="mt-1"
                defaultChecked={state.telemetryEnabled}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateState({ telemetryEnabled: e.target.checked })}
              />
              <label htmlFor="telemetry-optin" className="text-sm text-stone-700">
                <strong>Help improve OCR accuracy</strong>
                <p className="text-gray-600 mt-1">
                  Opt-in to share anonymous image data to help train better
                  citation recognition models. No personal information is
                  collected.
                </p>
              </label>
            </div>
          </div>

          <LegalDisclaimer variant="inline" className="mb-6" />

          {/* Camera Section */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <label className="block font-medium text-stone-700">
                Take Photo
              </label>
              {!cameraActive ? (
                <button
                  onClick={startCamera}
                  className="bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900 text-sm"
                >
                  Open Camera
                </button>
              ) : (
                <button
                  onClick={stopCamera}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm"
                >
                  Close Camera
                </button>
              )}
            </div>

            {cameraActive && (
              <div className="relative mb-4">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full rounded-lg bg-stone-900"
                />
                <button
                  onClick={capturePhoto}
                  className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white text-stone-800 w-16 h-16 rounded-full border-4 border-stone-300 hover:border-stone-500 flex items-center justify-center shadow-lg"
                >
                  <div className="w-12 h-12 rounded-full bg-stone-800" />
                </button>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 h-px bg-stone-200" />
            <span className="text-stone-500 text-sm">or</span>
            <div className="flex-1 h-px bg-stone-200" />
          </div>

          {/* File Upload Section */}
          <div className="mb-6">
            <label className="block mb-2 font-medium text-stone-700">
              Upload from Gallery
            </label>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              disabled={isProcessing}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-stone-100 file:text-stone-700 hover:file:bg-stone-200 disabled:opacity-50"
            />
            {isProcessing && (
              <p className="text-sm text-stone-500 mt-2">
                Processing images and extracting citation numbers...
              </p>
            )}
          </div>

          {/* OCR Results */}
          {ocrResults.some((r: OcrResult) => r.citationNumber) && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-medium text-green-800 mb-3">
                Citation Number Detected
              </h3>
              {ocrResults.map(
                (result: OcrResult, i: number) =>
                  result.citationNumber && (
                    <div
                      key={i}
                      className="flex items-center justify-between bg-white p-3 rounded mb-2"
                    >
                      <div>
                        <span className="text-sm text-gray-500">
                          Photo {i + 1}:
                        </span>{" "}
                        <code className="font-mono font-bold text-lg">
                          {result.citationNumber}
                        </code>
                        <span className="text-xs text-green-600 ml-2">
                          ({Math.round(result.confidence * 100)}% confidence)
                        </span>
                      </div>
                      <button
                        onClick={() => useOcrCitation(i)}
                        className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded hover:bg-green-200"
                      >
                        Use this
                      </button>
                    </div>
                  )
              )}
              <p className="text-xs text-green-700 mt-2">
                Please verify the detected citation number matches your ticket.
              </p>
            </div>
          )}

          {/* Manual citation input toggle */}
          <div className="mb-6">
            <button
              onClick={() => setShowManualInput(!showManualInput)}
              className="text-stone-600 hover:text-stone-800 text-sm underline"
            >
              {showManualInput ? "Hide" : "Enter"} citation number manually
            </button>

            {showManualInput && (
              <div className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={manualCitation}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setManualCitation(e.target.value.toUpperCase())}
                  placeholder="e.g., A12345678"
                  className="flex-1 px-4 py-2 border border-stone-300 rounded-lg font-mono"
                />
                <button
                  onClick={handleManualCitationSubmit}
                  className="bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-900"
                >
                  Save
                </button>
              </div>
            )}
          </div>

          {/* Photo preview */}
          {photos.length > 0 && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              {photos.map((photo: string, i: number) => (
                <div key={i} className="relative">
                  <img
                    src={photo}
                    alt={`Evidence ${i + 1}`}
                    className="w-full h-32 object-cover rounded border border-stone-200"
                  />
                  <button
                    onClick={() => removePhoto(i)}
                    className="absolute top-1 right-1 bg-stone-800 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-stone-900 transition-colors"
                  >
                    ×
                  </button>
                  {ocrResults[i]?.citationNumber && (
                    <div className="absolute bottom-1 left-1 bg-green-600 text-white text-xs px-2 py-0.5 rounded">
                      OCR
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          <div className="flex justify-between items-center">
            <Link
              href="/appeal"
              className="text-stone-600 hover:text-stone-800 transition-colors"
            >
              ← Back
            </Link>
            <button
              onClick={() => router.push("/appeal/review")}
              className="bg-stone-800 text-white px-6 py-3 rounded-lg hover:bg-stone-900 transition-colors font-medium"
            >
              Continue to Review →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Cleanup camera stream on unmount
useEffect(() => {
  return () => {
    // Cleanup camera stream when component unmounts
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };
}, []);

CameraPage.getLayout = function getLayout(page: React.ReactNode) {
  return page;
};
