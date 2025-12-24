/**
 * API Client for FightSFTickets.com
 * Handles all communication with the FastAPI backend
 * Based on legacy implementation patterns
 */

const API_URL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

// ============================================================
// TYPES
// ============================================================

export interface CitationValidationRequest {
  citation_number: string;
  license_plate?: string;
  violation_date: string;
}

export interface CitationValidationResponse {
  is_valid: boolean;
  error_message?: string;
  deadline?: string;
  is_past_deadline?: boolean;
  agency?: string;
}

export interface CheckoutData {
  citation_number: string;
  appeal_type: "standard" | "certified";
  user_name: string;
  user_address_line1: string;
  user_address_line2?: string;
  user_city: string;
  user_state: string;
  user_zip: string;
  violation_date: string;
  vehicle_info: string;
  appeal_reason: string;
  draft_text: string;
  license_plate?: string;
  email?: string;
  photos?: string[];
  signature_data?: string | null;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
  amount_total: number;
  currency: string;
  appeal_type: string;
  citation_number: string;
}

export interface SessionStatus {
  session_id: string;
  payment_status: "paid" | "unpaid" | "no_payment_required";
  amount_total: number;
  currency: string;
  citation_number?: string;
  appeal_type?: string;
  user_email?: string;
}

export interface StatementRefinementRequest {
  original_statement: string;
  citation_number: string;
  citation_type?: string;
  desired_tone?: string;
  max_length?: number;
}

export interface StatementRefinementResponse {
  refined_text?: string;
  letter_text?: string;
  success: boolean;
  error_message?: string;
}

// ============================================================
// API FUNCTIONS
// ============================================================

/**
 * Validate a citation number
 */
export async function validateCitation(
  data: CitationValidationRequest,
): Promise<CitationValidationResponse> {
  const response = await fetch(`${API_URL}/tickets/validate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    } catch {
      throw new Error(`Request failed: ${response.status}`);
    }
  }

  return await response.json();
}

/**
 * Create a Stripe checkout session
 * Returns a URL to redirect the user to Stripe
 */
export async function createCheckoutSession(
  data: CheckoutData,
): Promise<CheckoutResponse> {
  const response = await fetch(`${API_URL}/checkout/create-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  // Handle 202 Accepted status (server accepted request but response might be empty/different)
  if (response.status === 202) {
    try {
      const text = await response.text();
      if (text.trim() === "") {
        throw new Error(
          "Server accepted request but returned empty response (202 Accepted)",
        );
      }
      const data = JSON.parse(text);
      if (data.checkout_url) {
        return data;
      }
      throw new Error("Server returned 202 but no checkout_url in response");
    } catch (error) {
      throw new Error(
        `Payment request accepted but incomplete: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  if (!response.ok) {
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    } catch {
      const errorText = await response.text();
      throw new Error(errorText || `Request failed: ${response.status}`);
    }
  }

  try {
    return await response.json();
  } catch (error) {
    throw new Error(
      `Invalid response from server: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

/**
 * Get status of a checkout session
 */
export async function getSessionStatus(
  sessionId: string,
): Promise<SessionStatus> {
  const response = await fetch(`${API_URL}/checkout/session/${sessionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    } catch {
      throw new Error(`Request failed: ${response.status}`);
    }
  }

  return await response.json();
}

/**
 * Refine statement using AI
 */
export async function refineStatement(
  data: StatementRefinementRequest,
): Promise<StatementRefinementResponse> {
  const response = await fetch(`${API_URL}/api/statement/refine`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      original_statement: data.original_statement,
      citation_number: data.citation_number,
      citation_type: data.citation_type || "parking",
      desired_tone: data.desired_tone || "professional",
      max_length: data.max_length || 500,
    }),
  });

  if (!response.ok) {
    try {
      const errorData = await response.json();
      return {
        success: false,
        error_message: errorData.detail || `Request failed: ${response.status}`,
      };
    } catch {
      return {
        success: false,
        error_message: `Request failed: ${response.status}`,
      };
    }
  }

  const result = await response.json();
  return {
    success: true,
    refined_text: result.refined_statement || result.refined_text,
    letter_text: result.refined_statement || result.refined_text,
  };
}
