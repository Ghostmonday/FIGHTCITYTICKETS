"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "./lib/appeal-context";
import LegalDisclaimer from "../components/LegalDisclaimer";
import { apiClient } from "./lib/api-client";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Alert } from "../components/ui/Alert";

// Force dynamic rendering - this page uses client-side context
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
  {
    cityId: "nyc",
    name: "New York City",
    agency: "nyc",
    appealDeadlineDays: 30,
  },
  {
    cityId: "chicago",
    name: "Chicago",
    agency: "chicago",
    appealDeadlineDays: 20,
  },
  {
    cityId: "seattle",
    name: "Seattle",
    agency: "seattle",
    appealDeadlineDays: 20,
  },
  {
    cityId: "denver",
    name: "Denver",
    agency: "denver",
    appealDeadlineDays: 20,
  },
  {
    cityId: "portland",
    name: "Portland",
    agency: "portland",
    appealDeadlineDays: 10,
  },
  {
    cityId: "phoenix",
    name: "Phoenix",
    agency: "phoenix",
    appealDeadlineDays: 15,
  },
];

export default function Home() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [selectedCity, setSelectedCity] = useState("");
  const [citationNumber, setCitationNumber] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [violationDate, setViolationDate] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    citationId: string;
    detectedCity: string;
    selectedCityName: string;
    cityId: string;
    sectionId: string;
    appealDeadlineDays: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getCityDisplayName = (city: City): string => {
    return `${city.name} (${city.agency.toUpperCase()})`;
  };

  const handleValidateCitation = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationResult(null);
    setIsValidating(true);

    try {
      const data = await apiClient.post<{
        is_valid: boolean;
        citation_number: string;
        agency: string;
        deadline_date?: string;
        days_remaining?: number;
        is_past_deadline: boolean;
        is_urgent: boolean;
        error_message?: string;
        formatted_citation?: string;
        city_id?: string;
        section_id?: string;
        appeal_deadline_days: number;
        phone_confirmation_required: boolean;
        phone_confirmation_policy?: any;
        city_mismatch: boolean;
        selected_city_mismatch_message?: string;
      }>("/tickets/validate", {
        citation_number: citationNumber,
        license_plate: licensePlate || undefined,
        violation_date: violationDate || undefined,
        city_id: selectedCity,
      });

      if (!data.is_valid) {
        setError(
          data.error_message ||
            "We could not validate this citation. Please check the number and try again."
        );
        setIsValidating(false);
        return;
      }

      const detectedCity = CITIES.find((c) => c.cityId === selectedCity);
      const selectedCityName = detectedCity
        ? getCityDisplayName(detectedCity)
        : "Unknown City";

      // Store in context
      updateState({
        citationNumber: citationNumber,
        licensePlate: licensePlate,
        violationDate: violationDate,
        cityId: selectedCity,
        sectionId: detectedCity?.sectionId,
        appealDeadlineDays: detectedCity?.appealDeadlineDays,
      });

      setValidationResult({
        valid: true,
        citationId: data.citation_number,
        detectedCity: data.city_id || selectedCity,
        selectedCityName,
        cityId: data.city_id || selectedCity,
        sectionId: data.section_id || "",
        appealDeadlineDays: data.appeal_deadline_days || 21,
      });
    } catch (err) {
      setError(
        "We could not validate this citation. Please check the number and try again."
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleStartAppeal = () => {
    if (validationResult) {
      updateState({
        citationNumber: validationResult.citationId,
        cityId: validationResult.cityId,
        sectionId: validationResult.sectionId,
        appealDeadlineDays: validationResult.appealDeadlineDays,
      });
      router.push("/appeal");
    }
  };

  const formatAgency = (agency: string): string => {
    const agencies: Record<string, { name: string; sectionId: string }> = {
      sfmta: { name: "SFMTA", sectionId: "parking" },
      sfpd: { name: "SF Police", sectionId: "traffic" },
      sfsu: { name: "SFSU Police", sectionId: "parking" },
      sfmud: { name: "SF Municipal", sectionId: "utilities" },
      lapd: { name: "LAPD", sectionId: "parking" },
      ladot: { name: "LA DOT", sectionId: "parking" },
      nyc: { name: "NYC Finance", sectionId: "parking" },
      nypd: { name: "NY Police", sectionId: "traffic" },
      chicago: {
        name: "Chicago Finance",
        sectionId: "parking",
      },
      seattle: {
        name: "Seattle DOT",
        sectionId: "parking",
      },
      denver: {
        name: "Denver Public Works",
        sectionId: "parking",
      },
      portland: {
        name: "Portland Transportation",
        sectionId: "parking",
      },
    };
    return agencies[agency.toLowerCase()]?.name || agency;
  };

  return (
    <main className="min-h-screen bg-bg-page">
      {/* Hero Section */}
      <section className="bg-bg-surface border-b border-border animate-fade-in">
        <div className="max-w-4xl mx-auto px-4 py-16 sm:py-20 text-center">
          <h1 className="text-heading-xl text-text-primary mb-4 animate-slide-up">
            Got a parking ticket?
            <br className="hidden sm:block" />
            We help you prepare your appeal.
          </h1>
          <p className="text-body-lg text-text-secondary max-w-xl mx-auto mb-8 animate-slide-up stagger-1">
            Submit professionally formatted appeal documents in minutes. We
            handle the paperwork—you handle the details.
          </p>

          {/* Price and time badge */}
          <div className="inline-flex items-center gap-6 px-6 py-3 bg-bg-subtle rounded-full border border-border animate-fade-in stagger-2">
            <div className="text-center">
              <span className="text-2xl font-semibold text-text-primary">
                $39
              </span>
            </div>
            <div className="h-6 w-px bg-border" />
            <div className="text-center">
              <span className="text-body text-text-secondary">~5 minutes</span>
            </div>
          </div>

          {/* UPL Disclaimer - Short */}
          <p className="mt-6 text-caption text-text-muted animate-fade-in stagger-3">
            Document preparation only — not legal advice
          </p>
        </div>
      </section>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column: Citation Form */}
          <Card padding="lg" className="animate-slide-up">
            <h2 className="text-heading-md text-text-primary mb-6">
              Start Your Appeal
            </h2>

            <form onSubmit={handleValidateCitation} className="space-y-5">
              {/* City Selection */}
              <div>
                <label className="block text-body-sm font-medium text-text-secondary mb-2">
                  City where citation was issued *
                </label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full px-4 py-3 bg-bg-surface border border-border rounded-input text-text-primary focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all min-h-touch appearance-none cursor-pointer"
                  style={{
                    backgroundImage:
                      "url(\"data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e\")",
                    backgroundPosition: "right 12px center",
                    backgroundRepeat: "no-repeat",
                    backgroundSize: "20px",
                    paddingRight: "48px",
                  }}
                  required
                  disabled={isValidating}
                >
                  <option value="">Select a city...</option>
                  {CITIES.sort((a, b) => a.name.localeCompare(b.name)).map(
                    (city) => (
                      <option key={city.cityId} value={city.cityId}>
                        {getCityDisplayName(city)}
                      </option>
                    )
                  )}
                </select>
              </div>

              {/* Citation Number */}
              <div>
                <label className="block text-body-sm font-medium text-text-secondary mb-2">
                  Citation number *
                </label>
                <input
                  type="text"
                  value={citationNumber}
                  onChange={(e) => setCitationNumber(e.target.value)}
                  placeholder="e.g., 912345678, LA123456"
                  className="w-full px-4 py-3 bg-bg-surface border border-border rounded-input text-text-primary placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all min-h-touch"
                  required
                  disabled={isValidating}
                />
              </div>

              {/* Optional Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-body-sm font-medium text-text-secondary mb-2">
                    License plate
                  </label>
                  <input
                    type="text"
                    value={licensePlate}
                    onChange={(e) =>
                      setLicensePlate(e.target.value.toUpperCase())
                    }
                    placeholder="ABC123"
                    className="w-full px-4 py-3 bg-bg-surface border border-border rounded-input text-text-primary placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all min-h-touch"
                    disabled={isValidating}
                  />
                </div>
                <div>
                  <label className="block text-body-sm font-medium text-text-secondary mb-2">
                    Violation date
                  </label>
                  <input
                    type="date"
                    value={violationDate}
                    onChange={(e) => setViolationDate(e.target.value)}
                    className="w-full px-4 py-3 bg-bg-surface border border-border rounded-input text-text-primary focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all min-h-touch"
                    disabled={isValidating}
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <Alert
                  variant="error"
                  dismissible
                  onDismiss={() => setError(null)}
                >
                  {error}
                </Alert>
              )}

              {/* Validation Result */}
              {validationResult && (
                <Alert
                  variant="success"
                  title="Citation Validated"
                  dismissible
                  onDismiss={() => setValidationResult(null)}
                >
                  <span className="font-medium">
                    {formatAgency(validationResult.detectedCity)}
                  </span>{" "}
                  will process your appeal. Deadline:{" "}
                  {validationResult.appealDeadlineDays} days.
                </Alert>
              )}

              {/* Buttons */}
              <div className="pt-2">
                {!validationResult ? (
                  <Button
                    type="submit"
                    loading={isValidating}
                    fullWidth
                    disabled={isValidating}
                  >
                    {isValidating ? "Validating..." : "Validate Citation →"}
                  </Button>
                ) : (
                  <Button type="button" onClick={handleStartAppeal} fullWidth>
                    Begin Appeal →
                  </Button>
                )}
              </div>
            </form>
          </Card>

          {/* Right Column: How It Works */}
          <div className="space-y-6 animate-fade-in stagger-1">
            <h2 className="text-heading-md text-text-primary">How it works</h2>

            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-muted rounded-full flex items-center justify-center text-primary font-medium text-sm">
                1
              </div>
              <div>
                <h3 className="font-medium text-text-primary mb-1">
                  Enter your citation
                </h3>
                <p className="text-body-sm text-text-secondary">
                  Tell us where you got the ticket and provide the citation
                  number from your notice.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-muted rounded-full flex items-center justify-center text-primary font-medium text-sm">
                2
              </div>
              <div>
                <h3 className="font-medium text-text-primary mb-1">
                  Upload evidence
                </h3>
                <p className="text-body-sm text-text-secondary">
                  Add photos of signs, meters, or anything that supports your
                  appeal.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-muted rounded-full flex items-center justify-center text-primary font-medium text-sm">
                3
              </div>
              <div>
                <h3 className="font-medium text-text-primary mb-1">
                  Review and submit
                </h3>
                <p className="text-body-sm text-text-secondary">
                  We format your appeal professionally. You sign and pay, then
                  we mail it certified.
                </p>
              </div>
            </div>

            {/* Trust indicators */}
            <Card padding="md" className="mt-8">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2 text-body-sm text-text-secondary">
                  <svg
                    className="w-4 h-4 text-success"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Secure payment</span>
                </div>
                <div className="flex items-center gap-2 text-body-sm text-text-secondary">
                  <svg
                    className="w-4 h-4 text-success"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Certified mailing</span>
                </div>
                <div className="flex items-center gap-2 text-body-sm text-text-secondary">
                  <svg
                    className="w-4 h-4 text-success"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Document prep only</span>
                </div>
                <div className="flex items-center gap-2 text-body-sm text-text-secondary">
                  <svg
                    className="w-4 h-4 text-success"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>No legal advice</span>
                </div>
              </div>
            </Card>

            {/* Compact Disclaimer */}
            <div className="pt-4">
              <LegalDisclaimer variant="compact" />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-4 bg-bg-surface mt-12">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-body-sm text-text-muted">
          <p>© {new Date().getFullYear()} FightCityTickets.com</p>
          <div className="flex gap-6">
            <Link
              href="/terms"
              className="hover:text-text-primary transition-colors"
            >
              Terms
            </Link>
            <Link
              href="/privacy"
              className="hover:text-text-primary transition-colors"
            >
              Privacy
            </Link>
            <Link
              href="/what-we-are"
              className="hover:text-text-primary transition-colors"
            >
              What We Are
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
