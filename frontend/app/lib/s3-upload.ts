import { apiClient } from "./api-client";

/**
 * Uploads a photo to S3 if configured.
 *
 * @param file The file to upload
 * @param citationNumber Optional citation number for organization
 * @returns The public URL of the uploaded file, or null if S3 is not configured.
 * @throws Error if upload fails (network error, etc)
 */
export async function uploadPhoto(
  file: File,
  citationNumber?: string
): Promise<string | null> {
  try {
    // 1. Try to get presigned URL
    // This will throw 501 if S3 is not configured
    const presigned = await apiClient.post<{
      upload_url: string;
      key: string;
      public_url: string;
      photo_id: string;
    }>("/api/photos/presigned-url", {
      filename: file.name,
      content_type: file.type,
      citation_number: citationNumber,
    });

    // 2. Upload to S3
    // Use standard fetch to avoid custom headers from apiClient
    const uploadResponse = await fetch(presigned.upload_url, {
      method: "PUT",
      body: file,
      headers: {
        "Content-Type": file.type,
      },
    });

    if (!uploadResponse.ok) {
      throw new Error(`S3 upload failed: ${uploadResponse.statusText}`);
    }

    return presigned.public_url;
  } catch (error: any) {
    // Check if S3 is not configured (501 Not Implemented)
    // The apiClient throws an object that might have status property
    if (error.status === 501 || error.message?.includes("not configured")) {
      console.warn("S3 not configured, falling back to local storage");
      return null;
    }

    // Check for 400 (Bad Request) which might mean invalid file type
    if (error.status === 400) {
      throw new Error(error.message || "Invalid file");
    }

    console.error("Photo upload failed:", error);
    throw error;
  }
}
