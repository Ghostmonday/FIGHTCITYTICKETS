/**
 * OCR Helper for client-side citation number extraction
 *
 * Uses Tesseract.js for optical character recognition.
 * Provides fallback to manual entry if OCR fails.
 */

import { createWorker, Worker } from "tesseract.js";

// Citation number patterns by city
const CITATION_PATTERNS: RegExp[] = [
  /[A-Z]{1,2}\s*\d{6,8}/i, // SF: A12345678 or AB12345678
  /[A-Z]{1,2}\d{7,9}/i, // LA: A1234567
  /[A-Z]?\d{8,10}/i, // NYC: 1234567890
  /\d{8,12}/, // Numeric only
];

// Per-city OCR configuration hooks
const CITY_OCR_CONFIG: Record<string, { contrast: number; scale: number }> = {
  sf: { contrast: 1.2, scale: 2 }, // SF has high contrast tickets
  la: { contrast: 1.1, scale: 1.5 },
  nyc: { contrast: 1.0, scale: 2 },
  default: { contrast: 1.1, scale: 1.5 },
};

interface OcrResult {
  citationNumber?: string;
  confidence: number;
  rawText: string;
}

class OcrHelper {
  private worker: Worker | null = null;
  private isInitialized = false;

  /**
   * Initialize Tesseract worker with custom configuration
   */
  async initialize(cityId: string = "default"): Promise<void> {
    if (this.isInitialized && this.worker) {
      return;
    }

    const config = CITY_OCR_CONFIG[cityId] || CITY_OCR_CONFIG.default;

    this.worker = await createWorker("eng", 1, {
      logger: (m) => {
        if (process.env.NODE_ENV === "development") {
          console.log("OCR progress:", m);
        }
      },
    });

    // Apply city-specific preprocessing
    await this.worker.setParameters({
      tessedit_char_whitelist: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -",
    });

    this.isInitialized = true;
  }

  /**
   * Preprocess image for better OCR results
   */
  private preprocessImage(
    imageData: string,
    contrast: number,
    scale: number
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        if (!ctx) {
          reject(new Error("Could not get canvas context"));
          return;
        }

        // Scale up for better text recognition
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Get image data
        const imageDataObj = ctx.getImageData(
          0,
          0,
          canvas.width,
          canvas.height
        );
        const data = imageDataObj.data;

        // Apply contrast adjustment
        const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));

        for (let i = 0; i < data.length; i += 4) {
          const gray =
            0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
          const newGray = factor * (gray - 128) + 128;

          data[i] = Math.min(255, Math.max(0, newGray));
          data[i + 1] = Math.min(255, Math.max(0, newGray));
          data[i + 2] = Math.min(255, Math.max(0, newGray));
        }

        ctx.putImageData(imageDataObj, 0, 0);
        resolve(canvas.toDataURL("image/png"));
      };

      img.onerror = reject;
      img.src = imageData;
    });
  }

  /**
   * Extract text from image
   */
  async extractText(imageData: string): Promise<string> {
    if (!this.worker) {
      await this.initialize();
    }

    if (!this.worker) {
      throw new Error("Failed to initialize OCR worker");
    }

    const result = await this.worker.recognize(imageData);
    return result.data.text;
  }

  /**
   * Extract citation number from OCR text
   */
  extractCitationNumber(text: string): {
    number: string | null;
    confidence: number;
  } {
    const normalizedText = text.toUpperCase().replace(/\s+/g, " ");

    for (const pattern of CITATION_PATTERNS) {
      const match = normalizedText.match(pattern);
      if (match) {
        // Clean up the match
        const number = match[0].replace(/\s/g, "");
        return { number, confidence: 0.7 }; // Moderate confidence for pattern match
      }
    }

    // Try to find any 7-12 digit number as fallback
    const numericMatch = normalizedText.match(/\d{7,12}/);
    if (numericMatch) {
      return { number: numericMatch[0], confidence: 0.5 };
    }

    return { number: null, confidence: 0 };
  }

  /**
   * Full OCR pipeline with preprocessing and extraction
   */
  async extractTextFromImage(
    imageData: string,
    cityId: string = "default"
  ): Promise<OcrResult> {
    try {
      // Initialize worker if needed
      if (!this.isInitialized) {
        await this.initialize(cityId);
      }

      const config = CITY_OCR_CONFIG[cityId] || CITY_OCR_CONFIG.default;

      // Preprocess image for better OCR
      const processedImage = await this.preprocessImage(
        imageData,
        config.contrast,
        config.scale
      );

      // Run OCR
      const rawText = await this.extractText(processedImage);

      // Extract citation number
      const { number, confidence } = this.extractCitationNumber(rawText);

      return {
        citationNumber: number || undefined,
        confidence,
        rawText: rawText.trim(),
      };
    } catch (error) {
      console.error("OCR extraction failed:", error);
      return {
        confidence: 0,
        rawText: "",
      };
    }
  }

  /**
   * Cleanup worker resources
   */
  async terminate(): Promise<void> {
    if (this.worker) {
      await this.worker.terminate();
      this.worker = null;
      this.isInitialized = false;
    }
  }
}

// Export singleton instance
export const ocrHelper = new OcrHelper();

// Export individual functions for simple use cases
export async function extractTextFromImage(
  imageData: string,
  cityId?: string
): Promise<OcrResult> {
  return ocrHelper.extractTextFromImage(imageData, cityId);
}

// Export class for custom instances
export default OcrHelper;
