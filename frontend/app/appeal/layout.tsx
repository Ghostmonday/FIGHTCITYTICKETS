"use client";

import { useState } from "react";
import SaveProgressModal from "../../components/SaveProgressModal";

export default function AppealLayout({ children }: { children: React.ReactNode }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div className="relative">
        <button
          onClick={() => setIsModalOpen(true)}
          className="fixed top-24 right-4 z-40 btn-secondary text-sm px-3 py-1 shadow-md bg-white/90 backdrop-blur-sm"
          style={{
            borderColor: "var(--border)",
            color: "var(--text-secondary)"
          }}
        >
          Save & Resume Later
        </button>
        {children}
      </div>

      {isModalOpen && (
        <SaveProgressModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
}
