"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState, type ChangeEvent } from "react";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { Alert } from "../../../components/ui/Alert";
import { Button } from "../../../components/ui/Button";
import { Card } from "../../../components/ui/Card";
import { useAppeal } from "../../lib/appeal-context";
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
  const [manualCitation, setManualCitation] = useState(
    state.citationNumber || ""
  );
  const [showManualInput, setShowManualInput] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Start camera for live capture
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
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
      streamRef.current.getTracks().forEach((track) => track.stop());
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
    updateState({ photos: newPhotos });
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
    const newOcrResults = ocrResults.filter(
      (_: OcrResult, i: number) => i !== index
    );
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

  const applyOcrCitation = (index: number): void => {
    const result: OcrResult = ocrResults[index];
    if (result.citationNumber) {
      updateState({ citationNumber: result.citationNumber.toUpperCase() });
      setManualCitation(result.citationNumber);
    }
  };

  return (
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-heading-lg text-text-primary mb-2">
            Upload Evidence
          </h1>
          <p className="text-body text-text-secondary">
            Add photos of signs, meters, or anything that supports your appeal.
          </p>
        </div>

        <div className="space-y-6">
          {/* Upload Zone */}
          <Card padding="lg">
            <h2 className="text-heading-md text-text-primary mb-4">
              Add Photos
            </h2>
            <p className="text-body-sm text-text-secondary mb-6">
              Upload 2-5 photos. JPG or PNG, max 10MB each.
            </p>

            {/* Camera Section */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <label className="block font-medium text-text-primary">
                  Take Photo
                </label>
                {!cameraActive ? (
                  <Button variant="secondary" size="sm" onClick={startCamera}>
                    Open Camera
                  </Button>
                ) : (
                  <Button variant="secondary" size="sm" onClick={stopCamera}>
                    Close Camera
                  </Button>
                )}
              </div>

              {cameraActive && (
                <div className="relative mb-4">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full rounded-lg bg-text-primary"
                    style={{ minHeight: "250px", objectFit: "cover" }}
                  />
                  <button
                    onClick={capturePhoto}
                    className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-primary text-white w-16 h-16 rounded-full border-4 border-white shadow-lg flex items-center justify-center hover:bg-primary-hover transition-colors"
                  >
                    <div className="w-12 h-12 rounded-full bg-white" />
                  </button>
                </div>
              )}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1 h-px bg-border" />
              <span className="text-text-muted text-body-sm">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            {/* File Upload */}
            <div>
              <label className="block font-medium text-text-primary mb-2">
                Upload from Gallery
              </label>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileChange}
                disabled={isProcessing}
                className="block w-full text-body-sm text-text-secondary file:mr-4 file:py-2 file:px-4 file:rounded-input file:border-0 file:text-body file:font-medium file:bg-bg-subtle file:text-text-primary hover:file:bg-border disabled:opacity-50"
              />
              {isProcessing && (
                <p className="text-body-sm text-text-secondary mt-2">
                  Processing images...
                </p>
              )}
            </div>
          </Card>

          {/* OCR Results */}
          {ocrResults.some((r: OcrResult) => r.citationNumber) && (
            <Alert variant="success" title="Citation detected">
              {ocrResults.map(
                (result: OcrResult, i: number) =>
                  result.citationNumber && (
                    <div
                      key={i}
                      className="flex items-center justify-between bg-bg-surface p-3 rounded mt-2"
                    >
                      <div>
                        <span className="text-body-sm text-text-muted">
                          Photo {i + 1}:
                        </span>{" "}
                        <code className="font-mono font-medium text-text-primary">
                          {result.citationNumber}
                        </code>
                        <span className="text-caption text-success ml-2">
                          ({Math.round(result.confidence * 100)}% confidence)
                        </span>
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => applyOcrCitation(i)}
                      >
                        Use this
                      </Button>
                    </div>
                  )
              )}
              <p className="text-caption text-text-muted mt-2">
                Please verify the detected citation number matches your ticket.
              </p>
            </Alert>
          )}

          {/* Photo Preview */}
          {photos.length > 0 && (
            <Card padding="lg">
              <h3 className="text-heading-sm text-text-primary mb-4">
                Uploaded Photos ({photos.length})
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {photos.map((photo: string, i: number) => (
                  <div key={i} className="relative">
                    <img
                      src={photo}
                      alt={`Evidence ${i + 1}`}
                      className="w-full h-24 object-cover rounded border border-border"
                    />
                    <button
                      onClick={() => removePhoto(i)}
                      className="absolute top-1 right-1 bg-text-primary/80 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-text-primary transition-colors"
                      aria-label="Remove photo"
                    >
                      ×
                    </button>
                    {ocrResults[i]?.citationNumber && (
                      <div className="absolute bottom-1 left-1 bg-success text-white text-xs px-2 py-0.5 rounded">
                        OCR
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Manual citation input */}
          <Card padding="md">
            <button
              onClick={() => setShowManualInput(!showManualInput)}
              className="text-body text-primary hover:text-primary-hover font-medium"
            >
              {showManualInput ? "Hide" : "Enter"} citation number manually
            </button>

            {showManualInput && (
              <div className="mt-4 flex gap-3">
                <input
                  type="text"
                  value={manualCitation}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    setManualCitation(e.target.value.toUpperCase())
                  }
                  placeholder="e.g., A12345678"
                  className="flex-1 px-4 py-3 bg-bg-surface border border-border rounded-input text-text-primary placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 min-h-touch"
                />
                <Button onClick={handleManualCitationSubmit}>Save</Button>
              </div>
            )}
          </Card>

          {/* Telemetry opt-in */}
          <Card padding="md">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                className="mt-1 h-5 w-5 text-primary border-border rounded focus:ring-primary/50 cursor-pointer"
                defaultChecked={state.telemetryEnabled}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  updateState({ telemetryEnabled: e.target.checked })
                }
              />
              <div>
                <span className="font-medium text-text-primary">
                  Help improve citation recognition
                </span>
                <p className="text-body-sm text-text-secondary mt-1">
                  Opt-in to share anonymous image data to help train better
                  recognition models. No personal information is collected.
                </p>
              </div>
            </label>
          </Card>

          {/* Actions */}
          <div className="flex justify-between items-center pt-4">
            <Link
              href="/appeal"
              className="text-body text-text-secondary hover:text-text-primary transition-colors"
            >
              ← Back
            </Link>
            <Button onClick={() => router.push("/appeal/review")}>
              Continue to Review →
            </Button>
          </div>

          {/* Legal Disclaimer */}
          <LegalDisclaimer variant="compact" className="mt-6" />
        </div>
      </div>
    </main>
  );
}
