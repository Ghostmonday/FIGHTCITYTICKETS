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
          <h1 className="text-2xl font-bold mb-4">Upload Evidence Photos</h1>
          <p className="text-gray-600 mb-6">
            Add photos of parking signs, meters, or other evidence supporting
            your appeal.
          </p>
          <LegalDisclaimer variant="inline" className="mb-6" />

          <div className="mb-6">
            <label className="block mb-2 font-medium">Select Photos</label>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {photos.length > 0 && (
            <div className="grid grid-cols-3 gap-4 mb-6">
              {photos.map((photo, i) => (
                <div key={i} className="relative">
                  <img
                    src={photo}
                    alt={`Evidence ${i + 1}`}
                    className="w-full h-32 object-cover rounded"
                  />
                  <button
                    onClick={() => removePhoto(i)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex justify-between">
            <Link href="/appeal" className="text-gray-600 hover:text-gray-800">
              ← Back
            </Link>
            <button
              onClick={() => router.push("/appeal/review")}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Continue to Review →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
