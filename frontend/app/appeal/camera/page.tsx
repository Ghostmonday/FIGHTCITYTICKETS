"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState, type ChangeEvent } from "react";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { useAppeal } from "../../lib/appeal-context";
import { extractTextFromImage } from "../../lib/ocr-helper";
import { uploadPhoto } from "../../lib/s3-upload";

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

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraActive(true);
    } catch (error) {
      console.error("Failed to access camera:", error);
      alert("Unable to access camera. Please use file upload instead.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

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

  const base64ToFile = (base64: string, filename: string): File => {
    const arr = base64.split(",");
    const mime = arr[0].match(/:(.*?);/)?.[1] || "image/jpeg";
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  };

  const handlePhotoCapture = async (base64: string) => {
    setIsProcessing(true);
    let ocrResult: OcrResult = { confidence: 0, rawText: "" };

    try {
      // 1. Start upload
      const file = base64ToFile(base64, `photo_${Date.now()}.jpg`);
      const uploadPromise = uploadPhoto(file, state.citationNumber || undefined, state.cityId);

      // 2. Start OCR (parallel)
      const ocrPromise = extractTextFromImage(base64);

      // Wait for both
      const [uploadResult, ocr] = await Promise.all([uploadPromise, ocrPromise]);
      ocrResult = ocr;

      // 3. Update state with URL
      // If S3 upload succeeded, use the URL. If fallback (local), use base64 for display so it works in dev
      const photoUrl = uploadResult.is_s3 ? uploadResult.url : base64;

      const newPhotos = [...photos, photoUrl];
      setPhotos(newPhotos);
      setOcrResults([...ocrResults, ocrResult]);
      updateState({ photos: newPhotos });

    } catch (error) {
      console.error("Processing failed:", error);
      alert("Failed to process photo. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    setIsProcessing(true);

    const newPhotosList = [...photos];
    const newOcrResultsList = [...ocrResults];

    for (const file of Array.from(files)) {
      try {
        // Read for OCR
        const reader = new FileReader();
        const base64 = await new Promise<string>((resolve, reject) => {
          reader.onload = (event) => resolve(event.target?.result as string);
          reader.onerror = () => reject(new Error("Failed to read file"));
          reader.readAsDataURL(file);
        });

        // Start upload
        const uploadPromise = uploadPhoto(file, state.citationNumber || undefined, state.cityId);

        // Start OCR
        const ocrPromise = extractTextFromImage(base64);

        const [uploadResult, ocrResult] = await Promise.all([uploadPromise, ocrPromise]);

        const photoUrl = uploadResult.is_s3 ? uploadResult.url : base64;

        newPhotosList.push(photoUrl);
        newOcrResultsList.push(ocrResult);

      } catch (error) {
        console.error("File processing failed:", error);
      }
    }

    setPhotos(newPhotosList);
    setOcrResults(newOcrResultsList);
    updateState({ photos: newPhotosList });
    setIsProcessing(false);
  };

  const removePhoto = (index: number) => {
    const newPhotos = photos.filter((_: string, i: number) => i !== index);
    const newOcrResults = ocrResults.filter((_: OcrResult, i: number) => i !== index);
    setPhotos(newPhotos);
    setOcrResults(newOcrResults);
    updateState({ photos: newPhotos });
  };

  const handleManualCitationSubmit = () => {
    if (manualCitation.trim()) {
      updateState({ citationNumber: manualCitation.trim().toUpperCase() });
      setShowManualInput(false);
    }
  };

  const applyOcrCitation = (index: number) => {
    const result = ocrResults[index];
    if (result.citationNumber) {
      updateState({ citationNumber: result.citationNumber.toUpperCase() });
      setManualCitation(result.citationNumber);
    }
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] px-4 py-8 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 theme-transition" style={{ color: "var(--text-primary)" }}>
            Upload Evidence
          </h1>
          <p className="theme-transition" style={{ color: "var(--text-secondary)" }}>
            Add photos of signs, meters, or anything that supports your appeal
          </p>
        </div>

        {/* Upload Card */}
        <div className="card-step p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3" style={{ color: "var(--text-primary)" }}>Add Photos</h2>
          <p className="mb-4" style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            Upload 2-5 photos. JPG or PNG, max 10MB each.
          </p>

          {/* Camera */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>Take Photo</span>
              {!cameraActive ? (
                <button onClick={startCamera} className="btn-secondary text-sm py-2 px-4">Open Camera</button>
              ) : (
                <button onClick={stopCamera} className="btn-secondary text-sm py-2 px-4">Close Camera</button>
              )}
            </div>
            {cameraActive && (
              <div className="relative mb-4">
                <video ref={videoRef} autoPlay playsInline className="w-full rounded-lg" style={{ minHeight: "250px", objectFit: "cover", backgroundColor: "var(--text-muted)" }} />
                <button onClick={capturePhoto} className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 rounded-full border-4 flex items-center justify-center" style={{ backgroundColor: "var(--accent)", borderColor: "var(--bg-surface)" }}>
                  <div className="w-12 h-12 rounded-full bg-white" />
                </button>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
            <span style={{ color: "var(--text-muted)" }}>or</span>
            <div className="flex-1 h-px" style={{ backgroundColor: "var(--border)" }} />
          </div>

          {/* File Upload */}
          <div>
            <span style={{ color: "var(--text-primary)", fontWeight: 500, display: "block", marginBottom: "0.5rem" }}>Upload from Gallery</span>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              disabled={isProcessing}
              className="block w-full"
              style={{ color: "var(--text-secondary)" }}
            />
            {isProcessing && <p className="mt-2" style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>Processing images...</p>}
          </div>
        </div>

        {/* OCR Detected */}
        {ocrResults.some((r: OcrResult) => r.citationNumber) && (
          <div className="p-4 rounded-lg mb-6" style={{ backgroundColor: "#D1FAE5" }}>
            <h3 className="font-semibold mb-2" style={{ color: "#065F46" }}>Citation detected</h3>
            {ocrResults.map((result: OcrResult, i: number) =>
              result.citationNumber && (
                <div key={i} className="flex items-center justify-between mt-2 p-2 rounded" style={{ backgroundColor: "white" }}>
                  <div>
                    <span style={{ color: "#065F46", fontSize: "0.875rem" }}>Photo {i + 1}: </span>
                    <code style={{ color: "#065F46", fontFamily: "monospace", fontWeight: 500 }}>{result.citationNumber}</code>
                  </div>
                  <button onClick={() => applyOcrCitation(i)} className="text-sm px-3 py-1 rounded" style={{ backgroundColor: "#065F46", color: "white" }}>Use</button>
                </div>
              )
            )}
            <p style={{ color: "#065F46", fontSize: "0.75rem", marginTop: "0.5rem" }}>Please verify the detected citation number.</p>
          </div>
        )}

        {/* OCR Failed */}
        {ocrResults.some((r: OcrResult, i: number) => !r.citationNumber && photos[i]) && (
          <div className="p-4 rounded-lg mb-6" style={{ backgroundColor: "#FEE2E2" }}>
            <h3 className="font-semibold mb-2" style={{ color: "#991B1B" }}>Citation not detected</h3>
            {ocrResults.map((result: OcrResult, i: number) =>
              !result.citationNumber && photos[i] && (
                <div key={i} className="flex flex-col gap-2 mt-2 p-3 rounded" style={{ backgroundColor: "white" }}>
                  <div className="flex items-center justify-between">
                    <span style={{ color: "#991B1B", fontSize: "0.875rem" }}>Photo {i + 1}: Could not read citation number</span>
                  </div>
                  <div className="flex gap-2 mt-1">
                    <button
                      onClick={() => removePhoto(i)}
                      className="text-sm px-3 py-1 rounded border border-red-200 hover:bg-red-50"
                      style={{ color: "#991B1B" }}
                    >
                      Retake Photo
                    </button>
                    <button
                      onClick={() => setShowManualInput(true)}
                      className="text-sm px-3 py-1 rounded border border-red-200 hover:bg-red-50"
                      style={{ color: "#991B1B" }}
                    >
                      Enter Manually
                    </button>
                  </div>
                </div>
              )
            )}
            <p style={{ color: "#991B1B", fontSize: "0.75rem", marginTop: "0.5rem" }}>
              Please ensure the photo is clear and the citation number is visible, or enter it manually below.
            </p>
          </div>
        )}

        {/* Photo Preview */}
        {photos.length > 0 && (
          <div className="card-step p-6 mb-6">
            <h3 className="font-semibold mb-4" style={{ color: "var(--text-primary)" }}>Uploaded Photos ({photos.length})</h3>
            <div className="grid grid-cols-3 gap-4">
              {photos.map((photo: string, i: number) => (
                <div key={i} className="relative">
                  <img src={photo} alt={`Evidence ${i + 1}`} className="w-full h-24 object-cover rounded" style={{ border: "1px solid var(--border)" }} />
                  <button onClick={() => removePhoto(i)} className="absolute top-1 right-1 w-6 h-6 rounded-full flex items-center justify-center text-white" style={{ backgroundColor: "rgba(0,0,0,0.6)" }}>×</button>
                  {ocrResults[i]?.citationNumber && (
                    <div className="absolute bottom-1 left-1 text-xs px-2 py-0.5 rounded" style={{ backgroundColor: "#10B981", color: "white" }}>OCR</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Manual Citation */}
        <div className="card-step p-6 mb-6">
          <button onClick={() => setShowManualInput(!showManualInput)} style={{ color: "var(--accent)", fontWeight: 500 }}>
            {showManualInput ? "Hide" : "Enter"} citation number manually
          </button>
          {showManualInput && (
            <div className="mt-4 flex gap-3">
              <input
                type="text"
                value={manualCitation}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setManualCitation(e.target.value.toUpperCase())}
                placeholder="e.g., A12345678"
                className="input-strike flex-1"
              />
              <button onClick={handleManualCitationSubmit} className="btn-strike">Save</button>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-4 mb-6">
          <Link href="/appeal" className="btn-secondary flex-1">← Back</Link>
          <button onClick={() => router.push("/appeal/review")} className="btn-strike flex-1">Continue →</button>
        </div>

        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}
