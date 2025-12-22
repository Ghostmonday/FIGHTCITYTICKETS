"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "../../lib/appeal-context";

function CameraPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { state, updateState } = useAppeal();

  // State now holds base64 strings
  const [photos, setPhotos] = useState<string[]>(state.photos || []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const imageFiles = files.filter((file) => file.type.startsWith("image/"));

    if (imageFiles.length === 0) {
      alert("Please select image files only");
      return;
    }

    // Convert to Base64
    imageFiles.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          setPhotos((prev) => [...prev, e.target!.result as string]);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (index: number) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const handleContinue = () => {
    updateState({ photos });
    router.push(`/appeal/voice?type=${appealType}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/appeal"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Upload Photos (Optional)
          </h1>
          <p className="text-gray-600 mt-2">
            Step 2 of 5: Add photos that support your appeal
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="mt-4 text-lg font-medium text-gray-700">
              Click to upload photos
            </p>
            <p className="mt-2 text-sm text-gray-500">
              PNG, JPG, GIF up to 10MB each
            </p>
            <p className="mt-1 text-xs text-gray-400">
              Or drag and drop files here
            </p>
          </div>
        </div>

        {/* Photo Grid */}
        {photos.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Selected Photos ({photos.length})
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {photos.map((photo, index) => (
                <div key={index} className="relative group">
                  <img
                    src={photo}
                    alt={`Photo ${index + 1}`}
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => removePhoto(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                    aria-label="Remove photo"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* UPL Notice */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
          <p className="text-sm text-gray-700">
            <strong>Important:</strong> We do not recommend which photos to
            include. You decide what evidence supports your appeal. All photos
            will be included by default unless you deselect them later.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4">
          <Link
            href="/appeal"
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium text-center hover:bg-gray-50 transition-colors"
          >
            ← Back
          </Link>
          <button
            onClick={handleContinue}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Continue → {photos.length > 0 && `(${photos.length} photos)`}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function CameraPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CameraPageContent />
    </Suspense>
  );
}
