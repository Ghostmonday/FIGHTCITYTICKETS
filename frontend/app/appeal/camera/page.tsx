"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

export default function CameraPage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [photos, setPhotos] = useState<string[]>(state.photos || []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target?.result as string;
        setPhotos((prev) => [...prev, base64]);
        updateState({ photos: [...photos, base64] });
      };
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (index: number) => {
    const newPhotos = photos.filter((_, i) => i !== index);
    setPhotos(newPhotos);
    updateState({ photos: newPhotos });
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
            support your procedural appeal. The Clerical Engine™ will attach
            these to your submission.
          </p>
          <LegalDisclaimer variant="inline" className="mb-6" />

          <div className="mb-6">
            <label className="block mb-2 font-medium text-stone-700">
              Select Evidence Photos
            </label>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-stone-100 file:text-stone-700 hover:file:bg-stone-200"
            />
          </div>

          {photos.length > 0 && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              {photos.map((photo, i) => (
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
