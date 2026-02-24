import { apiClient } from "./api-client";
import { warn as logWarn } from "../../lib/logger";

interface PresignedUrlResponse {
  upload_url: string;
  key: string;
  public_url: string;
  photo_id: string;
}

interface UploadPhotoResult {
  photo_id: string;
  url: string;
  is_s3: boolean;
}

/**
 * Get a presigned URL for S3 upload
 */
export async function getPresignedUrl(
  file: File,
  citationNumber?: string
): Promise<PresignedUrlResponse> {
  return apiClient.post<PresignedUrlResponse>("/api/photos/presigned-url", {
    filename: file.name,
    content_type: file.type,
    citation_number: citationNumber,
  });
}

/**
 * Upload a file to S3 using a presigned URL
 */
export async function uploadToS3(
  file: File,
  uploadUrl: string
): Promise<void> {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    body: file,
    headers: {
      "Content-Type": file.type,
    },
  });

  if (!response.ok) {
    throw new Error(`S3 upload failed: ${response.statusText}`);
  }
}

/**
 * Upload a photo, attempting S3 first, then falling back to direct server upload
 */
export async function uploadPhoto(
  file: File,
  citationNumber?: string,
  cityId?: string
): Promise<UploadPhotoResult> {
  try {
    // Try to get S3 presigned URL
    const presigned = await getPresignedUrl(file, citationNumber);

    // Upload to S3
    await uploadToS3(file, presigned.upload_url);

    return {
      photo_id: presigned.photo_id,
      url: presigned.public_url,
      is_s3: true,
    };
  } catch (error: any) {
    // If S3 is not implemented (501) or not configured, fall back to legacy upload
    // Also fall back if presigned URL generation fails
    logWarn("S3 upload failed or not configured, falling back to direct upload:", error);

    // Legacy direct upload
    const uploadData = await apiClient.upload<{
      photo_id: string;
      filename: string;
      size: number;
    }>(
      "/api/photos/upload",
      file,
      {
        citation_number: citationNumber || "",
        city_id: cityId || "",
      }
    );

    return {
      photo_id: uploadData.photo_id,
      url: uploadData.photo_id, // Fallback: ID is used, but image won't load from URL
      is_s3: false,
    };
  }
}
