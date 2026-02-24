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
    it("should be an array", () => {
      expect(Array.isArray(CITIES)).toBe(true);
    });

    it("should contain valid city objects", () => {
      CITIES.forEach((city) => {
        expect(city).toHaveProperty("cityId");
        expect(city).toHaveProperty("name");
        expect(city).toHaveProperty("state");
        expect(city).toHaveProperty("stateCode");
      });
    });

    it("should contain San Francisco", () => {
      const sf = CITIES.find((c) => c.cityId === "us-ca-san_francisco");
      expect(sf).toBeDefined();
      expect(sf?.name).toBe("San Francisco");
      expect(sf?.stateCode).toBe("CA");
    });
  });

  describe("getCityById", () => {
    it("should return the correct city for a valid ID", () => {
      // Use the first city from the list to avoid hardcoding specific city dependency
      // (though we still rely on CITIES not being empty)
      const expectedCity = CITIES[0];
      const city = getCityById(expectedCity.cityId);
      expect(city).toBeDefined();
      expect(city).toEqual(expectedCity);
    });

    it("should return undefined for an invalid ID", () => {
      const city = getCityById("invalid-id-that-does-not-exist");
      expect(city).toBeUndefined();
    });
  });

  describe("getCityDisplayName", () => {
    it("should return the correctly formatted display name", () => {
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

      // Verify all states from CITIES are present
      const uniqueStates = new Set(CITIES.map(c => c.state));

      uniqueStates.forEach(state => {
        expect(grouped[state]).toBeDefined();
        expect(grouped[state].length).toBeGreaterThan(0);
        grouped[state].forEach((city) => {
          expect(city.state).toBe(state);
        });
      });
    });
  });

  describe("getSortedCities", () => {
    it("should return cities sorted alphabetically by name", () => {
      const sorted = getSortedCities();

      for (let i = 0; i < sorted.length - 1; i++) {
        const current = sorted[i].name;
        const next = sorted[i + 1].name;
        // localeCompare returns negative if current comes before next, 0 if equal, positive if after.
        // We want current <= next for ascending order.
        expect(current.localeCompare(next)).toBeLessThanOrEqual(0);
      }

      // Redundant check for robustness
      const names = sorted.map(c => c.name);
      const expectedNames = [...names].sort((a, b) => a.localeCompare(b));
      expect(names).toEqual(expectedNames);
    });

    it("should return a new array and not mutate the original CITIES", () => {
        const sorted = getSortedCities();
        expect(sorted).not.toBe(CITIES);
    });
  });
});
