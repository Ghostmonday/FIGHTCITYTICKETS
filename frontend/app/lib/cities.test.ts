import {
  CITIES,
  getCityById,
  getCityDisplayName,
  getCitiesByState,
  getSortedCities,
  City,
} from "./cities";

describe("City Logic", () => {
  describe("CITIES constant", () => {
    it("is an array of cities", () => {
      expect(Array.isArray(CITIES)).toBe(true);
      expect(CITIES.length).toBeGreaterThan(0);
    });

    it("contains San Francisco", () => {
      const sf = CITIES.find((c) => c.cityId === "us-ca-san_francisco");
      expect(sf).toBeDefined();
      expect(sf?.name).toBe("San Francisco");
      expect(sf?.stateCode).toBe("CA");
    });
  });

  describe("getCityById", () => {
    it("returns the city for a valid ID", () => {
      const city = getCityById("us-ca-san_francisco");
      expect(city).toBeDefined();
      expect(city?.name).toBe("San Francisco");
    });

    it("returns undefined for an invalid ID", () => {
      const city = getCityById("invalid-id");
      expect(city).toBeUndefined();
    });
  });

  describe("getCityDisplayName", () => {
    it("returns the formatted display name", () => {
      const mockCity: City = {
        cityId: "test-city",
        name: "Test City",
        state: "Test State",
        stateCode: "TS",
      };
      expect(getCityDisplayName(mockCity)).toBe("Test City, TS");
    });
  });

  describe("getCitiesByState", () => {
    it("groups cities by state", () => {
      const grouped = getCitiesByState();
      expect(grouped).toHaveProperty("California");
      expect(grouped["California"]).toBeInstanceOf(Array);

      const sfInGroup = grouped["California"].find(c => c.name === "San Francisco");
      expect(sfInGroup).toBeDefined();
    });

    it("contains entries for all cities", () => {
      const grouped = getCitiesByState();
      const totalCities = Object.values(grouped).reduce((acc, cities) => acc + cities.length, 0);
      expect(totalCities).toBe(CITIES.length);
    });
  });

  describe("getSortedCities", () => {
    it("returns cities sorted alphabetically by name", () => {
      const sorted = getSortedCities();

      // Check if it's sorted
      for (let i = 0; i < sorted.length - 1; i++) {
        const currentName = sorted[i].name;
        const nextName = sorted[i + 1].name;
        expect(currentName.localeCompare(nextName)).toBeLessThanOrEqual(0);
      }
    });

    it("returns a new array and does not mutate the original", () => {
      const sorted = getSortedCities();
      expect(sorted).not.toBe(CITIES);
      expect(sorted).toHaveLength(CITIES.length);
    });
  });
});
