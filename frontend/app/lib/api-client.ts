/**
 * API Client with retries, timeouts, and error handling
 * 
 * Provides a resilient wrapper around fetch with:
 * - Automatic retries with exponential backoff
 * - Configurable timeouts
 * - Graceful degradation for API outages
 * - Consistent error handling
 */

export interface ApiClientOptions {
  timeout?: number; // Request timeout in milliseconds (default: 30000)
  retries?: number; // Number of retry attempts (default: 3)
  retryDelay?: number; // Base delay between retries in ms (default: 1000)
  baseUrl?: string; // Base API URL (default: from env or localhost:8000)
}

export interface ApiError {
  message: string;
  status?: number;
  statusText?: string;
  isTimeout?: boolean;
  isNetworkError?: boolean;
}

class ApiClient {
  private baseUrl: string;
  private defaultTimeout: number;
  private defaultRetries: number;
  private defaultRetryDelay: number;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl =
      options.baseUrl ||
      process.env.NEXT_PUBLIC_API_BASE ||
      "http://localhost:8000";
    this.defaultTimeout = options.timeout || 30000; // 30 seconds
    this.defaultRetries = options.retries || 3;
    this.defaultRetryDelay = options.retryDelay || 1000;
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: ApiError): boolean {
    // Retry on network errors, timeouts, and 5xx errors
    if (error.isNetworkError || error.isTimeout) {
      return true;
    }
    if (error.status && error.status >= 500) {
      return true;
    }
    // Don't retry on 4xx errors (client errors)
    return false;
  }

  /**
   * Make API request with retries and timeout
   */
  async request<T = any>(
    endpoint: string,
    options: RequestInit = {},
    clientOptions?: ApiClientOptions
  ): Promise<T> {
    const timeout = clientOptions?.timeout || this.defaultTimeout;
    const retries = clientOptions?.retries ?? this.defaultRetries;
    const retryDelay = clientOptions?.retryDelay || this.defaultRetryDelay;

    const url = endpoint.startsWith("http")
      ? endpoint
      : `${this.baseUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

    let lastError: ApiError | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
          const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
              "Content-Type": "application/json",
              ...options.headers,
            },
          });

          clearTimeout(timeoutId);

          // Handle non-OK responses
          if (!response.ok) {
            const error: ApiError = {
              message: `API request failed: ${response.statusText}`,
              status: response.status,
              statusText: response.statusText,
            };

            // If not retryable or last attempt, throw
            if (!this.isRetryableError(error) || attempt === retries) {
              // Try to parse error message from response
              try {
                const errorData = await response.json();
                throw {
                  ...error,
                  message: errorData.detail || errorData.message || error.message,
                };
              } catch {
                throw error;
              }
            }

            lastError = error;
            // Wait before retrying
            if (attempt < retries) {
              const delay = retryDelay * Math.pow(2, attempt); // Exponential backoff
              await this.sleep(delay);
            }
            continue;
          }

          // Parse JSON response
          const data = await response.json();
          return data as T;
        } catch (fetchError: any) {
          clearTimeout(timeoutId);

          // Handle abort (timeout)
          if (fetchError.name === "AbortError") {
            const error: ApiError = {
              message: "Request timeout",
              isTimeout: true,
            };

            if (attempt === retries) {
              throw error;
            }

            lastError = error;
            if (attempt < retries) {
              const delay = retryDelay * Math.pow(2, attempt);
              await this.sleep(delay);
            }
            continue;
          }

          // Handle network errors
          if (
            fetchError instanceof TypeError ||
            fetchError.message?.includes("fetch")
          ) {
            const error: ApiError = {
              message: "Network error - service may be unavailable",
              isNetworkError: true,
            };

            if (attempt === retries) {
              throw error;
            }

            lastError = error;
            if (attempt < retries) {
              const delay = retryDelay * Math.pow(2, attempt);
              await this.sleep(delay);
            }
            continue;
          }

          // Re-throw other errors
          throw fetchError;
        }
      } catch (error: any) {
        // If this is the last attempt, throw the error
        if (attempt === retries) {
          throw error;
        }

        // Otherwise, continue to next retry
        lastError = error as ApiError;
        if (this.isRetryableError(error as ApiError)) {
          const delay = retryDelay * Math.pow(2, attempt);
          await this.sleep(delay);
        } else {
          // Non-retryable error, throw immediately
          throw error;
        }
      }
    }

    // Should never reach here, but TypeScript needs this
    throw lastError || new Error("Request failed after retries");
  }

  /**
   * GET request
   */
  async get<T = any>(
    endpoint: string,
    options?: RequestInit,
    clientOptions?: ApiClientOptions
  ): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" }, clientOptions);
  }

  /**
   * POST request
   */
  async post<T = any>(
    endpoint: string,
    body?: any,
    options?: RequestInit,
    clientOptions?: ApiClientOptions
  ): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        ...options,
        method: "POST",
        body: body ? JSON.stringify(body) : undefined,
      },
      clientOptions
    );
  }

  /**
   * PUT request
   */
  async put<T = any>(
    endpoint: string,
    body?: any,
    options?: RequestInit,
    clientOptions?: ApiClientOptions
  ): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        ...options,
        method: "PUT",
        body: body ? JSON.stringify(body) : undefined,
      },
      clientOptions
    );
  }

  /**
   * DELETE request
   */
  async delete<T = any>(
    endpoint: string,
    options?: RequestInit,
    clientOptions?: ApiClientOptions
  ): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" }, clientOptions);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for custom instances
export default ApiClient;
