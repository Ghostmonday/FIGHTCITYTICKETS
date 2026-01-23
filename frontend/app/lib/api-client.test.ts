/**
 * API Client tests for FIGHTCITYTICKETS.com
 */

import { apiClient } from "./api-client";

describe("API Client", () => {
  const mockFetch = jest.spyOn(global, "fetch");

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    mockFetch.mockRestore();
  });

  describe("get method", () => {
    it("makes a GET request to the correct endpoint", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );

      const result = await apiClient.get("/health");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/health"),
        expect.objectContaining({ method: "GET" })
      );
      expect(result).toEqual({ status: "ok" });
    });

    it("throws error on failed GET request", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({ error: "Not found" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        })
      );

      await expect(apiClient.get("/nonexistent")).rejects.toThrow();
    });
  });

  describe("post method", () => {
    it("makes a POST request with correct headers", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({ success: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );

      const result = await apiClient.post("/tickets/validate", {
        citation_number: "912345678",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/tickets/validate"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
        })
      );
      expect(result).toEqual({ success: true });
    });

    it("sends data in request body", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({ is_valid: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );

      await apiClient.post("/tickets/validate", {
        citation_number: "912345678",
        city_id: "sf",
      });

      const fetchCall = mockFetch.mock.calls[0];
      const body = JSON.parse(fetchCall[1].body);
      expect(body.citation_number).toBe("912345678");
      expect(body.city_id).toBe("sf");
    });
  });

  describe("error handling", () => {
    it("handles network errors gracefully", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      await expect(apiClient.get("/health")).rejects.toThrow("Network error");
    });

    it("throws on server errors", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({ error: "Internal server error" }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        })
      );

      await expect(apiClient.get("/health")).rejects.toThrow();
    });
  });
});
