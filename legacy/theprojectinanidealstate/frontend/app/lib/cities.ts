export interface City {
  cityId: string;
  name: string;
  state: string;
  stateCode: string;
}

/**
 * All supported cities for parking ticket appeals.
 * This list matches the cities configured in the backend city registry.
 */
export const CITIES: City[] = [
  // California
  {
    cityId: "us-ca-san_francisco",
    name: "San Francisco",
    state: "California",
    stateCode: "CA",
  },
  {
    cityId: "us-ca-los_angeles",
    name: "Los Angeles",
    state: "California",
    stateCode: "CA",
  },
  {
    cityId: "us-ca-san_diego",
    name: "San Diego",
    state: "California",
    stateCode: "CA",
  },
  {
    cityId: "us-ca-oakland",
    name: "Oakland",
    state: "California",
    stateCode: "CA",
  },
  {
    cityId: "us-ca-sacramento",
    name: "Sacramento",
    state: "California",
    stateCode: "CA",
  },
  // Arizona
  {
    cityId: "us-az-phoenix",
    name: "Phoenix",
    state: "Arizona",
    stateCode: "AZ",
  },
  // Colorado
  {
    cityId: "us-co-denver",
    name: "Denver",
    state: "Colorado",
    stateCode: "CO",
  },
  // Florida
  {
    cityId: "us-fl-miami",
    name: "Miami",
    state: "Florida",
    stateCode: "FL",
  },
  // Georgia
  {
    cityId: "us-ga-atlanta",
    name: "Atlanta",
    state: "Georgia",
    stateCode: "GA",
  },
  // Illinois
  {
    cityId: "us-il-chicago",
    name: "Chicago",
    state: "Illinois",
    stateCode: "IL",
  },
  // Kentucky
  {
    cityId: "us-ky-louisville",
    name: "Louisville",
    state: "Kentucky",
    stateCode: "KY",
  },
  // Massachusetts
  {
    cityId: "us-ma-boston",
    name: "Boston",
    state: "Massachusetts",
    stateCode: "MA",
  },
  // Maryland
  {
    cityId: "us-md-baltimore",
    name: "Baltimore",
    state: "Maryland",
    stateCode: "MD",
  },
  // Michigan
  {
    cityId: "us-mi-detroit",
    name: "Detroit",
    state: "Michigan",
    stateCode: "MI",
  },
  // Minnesota
  {
    cityId: "us-mn-minneapolis",
    name: "Minneapolis",
    state: "Minnesota",
    stateCode: "MN",
  },
  // North Carolina
  {
    cityId: "us-nc-charlotte",
    name: "Charlotte",
    state: "North Carolina",
    stateCode: "NC",
  },
  // New York
  {
    cityId: "us-ny-new_york",
    name: "New York",
    state: "New York",
    stateCode: "NY",
  },
  // Oregon
  {
    cityId: "us-or-portland",
    name: "Portland",
    state: "Oregon",
    stateCode: "OR",
  },
  // Pennsylvania
  {
    cityId: "us-pa-philadelphia",
    name: "Philadelphia",
    state: "Pennsylvania",
    stateCode: "PA",
  },
  // Texas
  {
    cityId: "us-tx-dallas",
    name: "Dallas",
    state: "Texas",
    stateCode: "TX",
  },
  {
    cityId: "us-tx-houston",
    name: "Houston",
    state: "Texas",
    stateCode: "TX",
  },
  // Utah
  {
    cityId: "us-ut-salt_lake_city",
    name: "Salt Lake City",
    state: "Utah",
    stateCode: "UT",
  },
  // Washington
  {
    cityId: "us-wa-seattle",
    name: "Seattle",
    state: "Washington",
    stateCode: "WA",
  },
];

/**
 * Get city by cityId
 */
export function getCityById(cityId: string): City | undefined {
  return CITIES.find((city) => city.cityId === cityId);
}

/**
 * Get display name for a city
 */
export function getCityDisplayName(city: City): string {
  return `${city.name}, ${city.stateCode}`;
}

/**
 * Get all cities grouped by state
 */
export function getCitiesByState(): Record<string, City[]> {
  const grouped: Record<string, City[]> = {};
  for (const city of CITIES) {
    if (!grouped[city.state]) {
      grouped[city.state] = [];
    }
    grouped[city.state].push(city);
  }
  return grouped;
}

/**
 * Sort cities alphabetically by name
 */
export function getSortedCities(): City[] {
  return [...CITIES].sort((a, b) => a.name.localeCompare(b.name));
}

