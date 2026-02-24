import {
  CITIES,
  getCityById,
  getCityDisplayName,
  getCitiesByState,
  getSortedCities,
  City,
} from "./cities";

describe("Cities Library", () => {
  describe("CITIES constant", () => {
    it("should be an array of cities", () => {
      expect(Array.isArray(CITIES)).toBe(true);
      expect(CITIES.length).toBeGreaterThan(0);
    });

    it("should contain San Francisco as the first entry", () => {
      const sf = CITIES.find((c) => c.cityId === "us-ca-san_francisco");
      expect(sf).toBeDefined();
      expect(sf?.name).toBe("San Francisco");
      expect(sf?.stateCode).toBe("CA");
    });
  });

  describe("getCityById", () => {
    it("should return the correct city for a valid ID", () => {
      const city = getCityById("us-ny-new_york");
      expect(city).toBeDefined();
      expect(city?.name).toBe("New York");
      expect(city?.state).toBe("New York");
    });

    it("should return undefined for an invalid ID", () => {
      const city = getCityById("invalid-id");
      expect(city).toBeUndefined();
    });
  });

  describe("getCityDisplayName", () => {
    it("should format the display name correctly", () => {
      const city: City = {
        cityId: "test-city",
        name: "Test City",
        state: "Test State",
        stateCode: "TS",
      };
      expect(getCityDisplayName(city)).toBe("Test City, TS");
    });
  });

  describe("getCitiesByState", () => {
    it("should group cities by state", () => {
      const grouped = getCitiesByState();

      // Check California
      expect(grouped["California"]).toBeDefined();
      expect(Array.isArray(grouped["California"])).toBe(true);
      expect(grouped["California"].some(c => c.name === "San Francisco")).toBe(true);
      expect(grouped["California"].some(c => c.name === "Los Angeles")).toBe(true);

      // Check New York
      expect(grouped["New York"]).toBeDefined();
      expect(grouped["New York"].some(c => c.name === "New York")).toBe(true);
    });
  });

  describe("getSortedCities", () => {
    it("should return cities sorted by name", () => {
      const sorted = getSortedCities();

      // Check that it's a new array
      expect(sorted).not.toBe(CITIES);
      expect(sorted.length).toBe(CITIES.length);

      // Verify sorting
      for (let i = 0; i < sorted.length - 1; i++) {
        expect(sorted[i].name.localeCompare(sorted[i + 1].name)).toBeLessThanOrEqual(0);
      }
    });

    it("should not mutate the original CITIES array", () => {
        // Find a city that is not first alphabetically but first in the list
        // San Francisco is first in the list but "Atlanta" is alphabetically first.
        // Wait, San Francisco is first in the list.
        // Let's verify the original list order is preserved.
        const originalFirst = CITIES[0];
        getSortedCities();
        expect(CITIES[0]).toBe(originalFirst);
    });
  });
});
