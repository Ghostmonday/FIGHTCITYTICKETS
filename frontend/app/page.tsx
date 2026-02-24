"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "./lib/appeal-context";
import { apiClient } from "./lib/api-client";
import LegalDisclaimer from "../components/LegalDisclaimer";

// Force dynamic rendering
export const dynamic = "force-dynamic";

interface City {
  cityId: string;
  name: string;
  agency: string;
  sectionId?: string;
  appealDeadlineDays: number;
}

const CITIES: City[] = [
  { cityId: "sf", name: "San Francisco", agency: "sf", appealDeadlineDays: 21 },
  { cityId: "la", name: "Los Angeles", agency: "la", appealDeadlineDays: 21 },
  { cityId: "nyc", name: "New York City", agency: "nyc", appealDeadlineDays: 30 },
  { cityId: "chicago", name: "Chicago", agency: "chicago", appealDeadlineDays: 20 },
  { cityId: "seattle", name: "Seattle", agency: "seattle", appealDeadlineDays: 20 },
  { cityId: "denver", name: "Denver", agency: "denver", appealDeadlineDays: 20 },
  { cityId: "portland", name: "Portland", agency: "portland", appealDeadlineDays: 10 },
  { cityId: "phoenix", name: "Phoenix", agency: "phoenix", appealDeadlineDays: 15 },
];

type Step = "citation" | "upload" | "success";

export default function Home() {
  const router = useRouter();
  const { state, updateState } = useAppeal();

  // UI State
  const [currentStep, setCurrentStep] = useState<Step>("citation");
  const [progress, setProgress] = useState(33);
  const [selectedCity, setSelectedCity] = useState("");
  const [citationNumber, setCitationNumber] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Upload State
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleValidateCitation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCity || !citationNumber) return;

    setError(null);
    setIsValidating(true);

    try {
      const data = await apiClient.post<{
        is_valid: boolean;
        citation_number: string;
        agency: string;
        city_id?: string;
        section_id?: string;
        appeal_deadline_days: number;
        error_message?: string;
      }>("/tickets/validate", {
        citation_number: citationNumber,
        license_plate: licensePlate || undefined,
        city_id: selectedCity,
      });

      if (!data.is_valid) {
        setError(data.error_message || "Could not validate citation. Please check and try again.");
        setIsValidating(false);
        return;
      }

      // Store in context
      updateState({
        citationNumber: citationNumber,
        licensePlate: licensePlate,
        cityId: selectedCity,
        sectionId: data.section_id,
        appealDeadlineDays: data.appeal_deadline_days,
      });

      // Move to upload step
      setProgress(66);
      setCurrentStep("upload");
    } catch (err) {
      setError("Could not validate citation. Please try again.");
    } finally {
      setIsValidating(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setUploadedFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setUploadedFile(file);
    }
  };

  const handleGenerateDefense = () => {
    if (selectedCity && citationNumber) {
      updateState({
        citationNumber,
        licensePlate,
        cityId: selectedCity,
      });
      router.push("/appeal");
    }
  };

  const handleBack = () => {
    if (currentStep === "upload") {
      setProgress(33);
      setCurrentStep("citation");
    }
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] flex flex-col items-center justify-center px-4 py-8 theme-transition">
      {/* Progress Bar */}
      <div className="w-full max-w-lg mb-12 animate-fade-in">
        <div className="progress-bar">
          <div
            className="progress-bar-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-sm" style={{ color: "var(--text-muted)" }}>
          <span>Citation</span>
          <span>Upload</span>
          <span>Defense</span>
        </div>
      </div>

      {/* Step Content */}
      <div className="w-full max-w-lg step-content">

        {/* STEP 1: Citation Number */}
        {currentStep === "citation" && (
          <div className="animate-slide-up">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extralight mb-8 tracking-tight text-center leading-tight theme-transition" style={{ color: "var(--text-primary)" }}>
              They Demand Perfection.<br className="hidden sm:block" /> We Deliver It.
            </h1>
            <p className="text-xl sm:text-2xl mb-3 font-light text-center tracking-wide theme-transition" style={{ color: "var(--text-secondary)" }}>
              A parking citation is a procedural document.
            </p>
            <p className="text-lg sm:text-xl mb-10 text-center theme-transition" style={{ color: "var(--text-secondary)" }}>
              Municipalities win through clerical precision.<br className="hidden sm:block" />
              <span className="font-normal" style={{ color: "var(--text-primary)" }}>We make their weapon our shield.</span>
            </p>
            <div className="mt-6 mb-12 text-sm text-center font-medium theme-transition" style={{ color: "var(--text-muted)" }}>
              We aren&apos;t lawyers. We&apos;re paperwork experts. And in a bureaucracy, paperwork is power.
            </div>

            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extralight mb-4 tracking-tight text-center theme-transition" style={{ color: "var(--text-primary)" }}>
              Due Process as a Service
            </h2>
            <p className="text-base sm:text-lg max-w-lg mx-auto font-light text-center mb-10 theme-transition" style={{ color: "var(--text-secondary)" }}>
              We don&apos;t offer legal advice. We deliver procedural perfection—formatted exactly how the city requires it.
            </p>

            <h3 className="text-xl font-medium text-center mb-6 theme-transition" style={{ color: "var(--text-primary)" }}>
              What&apos;s the Citation Number?
            </h3>


            <form onSubmit={handleValidateCitation} className="space-y-6">
              {/* City Selection */}
              <div>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="input-strike"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23A3A3A3' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: "right 16px center",
                    backgroundRepeat: "no-repeat",
                    backgroundSize: "24px",
                    paddingRight: "56px",
                  }}
                  required
                  disabled={isValidating}
                >
                  <option value="">Select your city...</option>
                  {CITIES.sort((a, b) => a.name.localeCompare(b.name)).map((city) => (
                    <option key={city.cityId} value={city.cityId}>
                      {city.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Citation Input */}
              <div>
                <input
                  type="text"
                  value={citationNumber}
                  onChange={(e) => setCitationNumber(e.target.value)}
                  placeholder="e.g., 912345678"
                  className="input-strike text-center text-2xl tracking-wider"
                  style={{ fontSize: "2rem", letterSpacing: "0.1em" }}
                  required
                  disabled={isValidating}
                />
              </div>

              {/* Optional License Plate */}
              <div>
                <input
                  type="text"
                  value={licensePlate}
                  onChange={(e) => setLicensePlate(e.target.value.toUpperCase())}
                  placeholder="License plate (optional)"
                  className="input-strike text-center"
                  disabled={isValidating}
                />
              </div>

              {/* Error */}
              {error && (
                <p className="text-center" style={{ color: "#DC2626" }}>
                  {error}
                </p>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isValidating || !selectedCity || !citationNumber}
                className="btn-strike w-full"
              >
                {isValidating ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Validating...
                  </span>
                ) : (
                  "Submit Appeal →"
                )}
              </button>
            </form>
          </div>
        )}

        {/* STEP 2: Upload Photo */}
        {currentStep === "upload" && (
          <div className="animate-slide-up">
            <h1 className="text-display text-center mb-4 theme-transition" style={{ color: "var(--text-primary)" }}>
              Upload Photo<br />of Ticket
            </h1>
            <p className="text-lg text-center mb-10 theme-transition" style={{ color: "var(--text-secondary)" }}>
              {citationNumber} — {CITIES.find(c => c.cityId === selectedCity)?.name}
            </p>

            <div
              className={`drop-zone ${isDragging ? "active" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              {uploadedFile ? (
                <div className="flex flex-col items-center gap-4">
                  <svg className="w-16 h-16" style={{ color: "var(--accent)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-lg font-medium" style={{ color: "var(--text-primary)" }}>
                    {uploadedFile.name}
                  </p>
                  <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    Click to change
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <svg className="w-16 h-16" style={{ color: "var(--text-muted)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p className="text-lg font-medium" style={{ color: "var(--text-secondary)" }}>
                    Drop photo here
                  </p>
                  <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    or click to browse
                  </p>
                </div>
              )}
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            {/* Navigation */}
            <div className="flex gap-4 mt-8">
              <button
                onClick={handleBack}
                className="btn-secondary flex-1"
              >
                ← Back
              </button>
              <button
                onClick={handleGenerateDefense}
                className="btn-strike flex-1"
              >
                Generate Defense →
              </button>
            </div>
          </div>
        )}

      </div>

      {/* Disclaimer */}
      <div className="mt-16 text-center">
        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}
