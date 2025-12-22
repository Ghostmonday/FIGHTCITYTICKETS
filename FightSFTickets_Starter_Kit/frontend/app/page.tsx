"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Fight Your SF Parking Ticket
          </h1>
          <p className="text-xl md:text-2xl text-gray-700 mb-8">
            We handle the paperwork. You save time and money.
          </p>
          <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
            Appeal your San Francisco parking ticket with AI-powered letter
            generation and automatic mail delivery. Professional, fast, and
            affordable.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/appeal"
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-colors shadow-lg"
            >
              Start Your Appeal
            </Link>
            <Link
              href="/how-it-works"
              className="bg-white hover:bg-gray-50 text-indigo-600 font-semibold py-4 px-8 rounded-lg text-lg transition-colors border-2 border-indigo-600"
            >
              How It Works
            </Link>
          </div>
        </div>
      </section>

      {/* 3-Step Process */}
      <section className="container mx-auto px-4 py-16 bg-white">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
          Simple 3-Step Process
        </h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center p-6">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">1</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              Enter Your Citation
            </h3>
            <p className="text-gray-600">
              Provide your citation number, upload photos, and record your
              story. Our AI helps format your appeal letter.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">2</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              Review & Pay
            </h3>
            <p className="text-gray-600">
              Review your professionally formatted appeal letter, make any
              edits, and choose standard or certified mail delivery.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-indigo-600">3</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              We Mail It
            </h3>
            <p className="text-gray-600">
              We print and mail your appeal letter directly to SFMTA. You
              receive tracking information and can monitor delivery.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-16 bg-gray-50">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
          Choose Your Service Level
        </h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Standard Mail */}
          <div className="bg-white rounded-lg shadow-lg p-8 border-2 border-gray-200">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Standard Mail
            </h3>
            <div className="mb-4">
              <span className="text-4xl font-bold text-indigo-600">$9</span>
              <span className="text-gray-600 ml-2">one-time</span>
            </div>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  AI-generated appeal letter
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Photo upload and inclusion
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Standard mail delivery (~$1)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Delivery tracking
                </span>
              </li>
            </ul>
            <Link
              href="/appeal?type=standard"
              className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg text-center transition-colors"
            >
              Choose Standard
            </Link>
          </div>

          {/* Certified Mail */}
          <div className="bg-white rounded-lg shadow-lg p-8 border-2 border-indigo-600 relative">
            <div className="absolute top-0 right-0 bg-indigo-600 text-white px-4 py-1 rounded-bl-lg text-sm font-semibold">
              RECOMMENDED
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Certified Mail
            </h3>
            <div className="mb-4">
              <span className="text-4xl font-bold text-indigo-600">$19</span>
              <span className="text-gray-600 ml-2">one-time</span>
            </div>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Everything in Standard
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Certified mail delivery (~$10.50)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Proof of delivery
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-gray-700">
                  Higher success rate
                </span>
              </li>
            </ul>
            <Link
              href="/appeal?type=certified"
              className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg text-center transition-colors"
            >
              Choose Certified
            </Link>
          </div>
        </div>
      </section>

      {/* UPL Disclaimer Footer */}
      <footer className="bg-gray-900 text-gray-300 py-8 mt-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-yellow-900 bg-opacity-30 border-l-4 border-yellow-500 p-4 mb-6">
              <p className="text-sm font-semibold text-yellow-200 mb-2">
                ⚠️ Important Legal Notice
              </p>
              <p className="text-sm">
                FightSFTickets is not a law firm and does not provide legal
                advice. We are a document preparation service that helps you
                format and submit your own appeal. We do not recommend specific
                evidence, promise outcomes, or provide legal representation. You
                are responsible for the content of your appeal.
              </p>
            </div>
            <div className="flex flex-col md:flex-row justify-between items-center text-sm">
              <div>
                <p>© 2025 FightSFTickets. All rights reserved.</p>
              </div>
              <div className="flex gap-6 mt-4 md:mt-0">
                <Link href="/terms" className="hover:text-white">
                  Terms of Service
                </Link>
                <Link href="/privacy" className="hover:text-white">
                  Privacy Policy
                </Link>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
