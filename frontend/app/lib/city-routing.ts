// City routing utilities for FIGHTCITYTICKETS.com
// Maps URL slugs (SF, SD, NYC) to internal city identifiers

export interface CityMapping {
  slug: string; // URL slug (SF, SD, NYC)
  internalId: string; // Internal ID (san_francisco, san_diego, nyc)
  cityId: string; // Backend city ID (us-ca-san_francisco)
  name: string; // Display name
  state: string; // State code
}

// City slug mappings - uppercase slugs for URLs
export const CITY_SLUG_MAP: Record<string, CityMapping> = {
  SF: {
    slug: "SF",
    internalId: "san_francisco",
    cityId: "us-ca-san_francisco",
    name: "San Francisco",
    state: "CA",
  },
  SD: {
    slug: "SD",
    internalId: "san_diego",
    cityId: "us-ca-san_diego",
    name: "San Diego",
    state: "CA",
  },
  NYC: {
    slug: "NYC",
    internalId: "nyc",
    cityId: "us-ny-new_york",
    name: "New York City",
    state: "NY",
  },
  LA: {
    slug: "LA",
    internalId: "los_angeles",
    cityId: "us-ca-los_angeles",
    name: "Los Angeles",
    state: "CA",
  },
  SJ: {
    slug: "SJ",
    internalId: "san_jose",
    cityId: "us-ca-san_jose",
    name: "San Jose",
    state: "CA",
  },
  CHI: {
    slug: "CHI",
    internalId: "chicago",
    cityId: "us-il-chicago",
    name: "Chicago",
    state: "IL",
  },
  SEA: {
    slug: "SEA",
    internalId: "seattle",
    cityId: "us-wa-seattle",
    name: "Seattle",
    state: "WA",
  },
  PHX: {
    slug: "PHX",
    internalId: "phoenix",
    cityId: "us-az-phoenix",
    name: "Phoenix",
    state: "AZ",
  },
  DEN: {
    slug: "DEN",
    internalId: "denver",
    cityId: "us-co-denver",
    name: "Denver",
    state: "CO",
  },
  DAL: {
    slug: "DAL",
    internalId: "dallas",
    cityId: "us-tx-dallas",
    name: "Dallas",
    state: "TX",
  },
  HOU: {
    slug: "HOU",
    internalId: "houston",
    cityId: "us-tx-houston",
    name: "Houston",
    state: "TX",
  },
  PHI: {
    slug: "PHI",
    internalId: "philadelphia",
    cityId: "us-pa-philadelphia",
    name: "Philadelphia",
    state: "PA",
  },
  PDX: {
    slug: "PDX",
    internalId: "portland",
    cityId: "us-or-portland",
    name: "Portland",
    state: "OR",
  },
  SLC: {
    slug: "SLC",
    internalId: "salt_lake_city",
    cityId: "us-ut-salt_lake_city",
    name: "Salt Lake City",
    state: "UT",
  },
};

// Reverse mapping: internal ID -> slug
export const INTERNAL_TO_SLUG: Record<string, string> = {};
Object.entries(CITY_SLUG_MAP).forEach(([slug, mapping]) => {
  INTERNAL_TO_SLUG[mapping.internalId] = slug;
  INTERNAL_TO_SLUG[mapping.cityId] = slug;
});

// Geolocation-based city detection
export interface GeoLocation {
  city?: string;
  region?: string; // State code
  country?: string;
}

// Map common city/region names to city slugs
export function detectCityFromLocation(geo: GeoLocation): string | null {
  const city = geo.city?.toLowerCase() || "";
  const region = geo.region?.toUpperCase() || "";

  // San Francisco Bay Area
  if (
    city.includes("san francisco") ||
    (city.includes("sf") && region === "CA")
  ) {
    return "SF";
  }
  if (city.includes("san jose") || city.includes("sanjose")) {
    return "SJ";
  }
  if (city.includes("san diego") || city.includes("sandiego")) {
    return "SD";
  }
  if (
    city.includes("los angeles") ||
    city.includes("losangeles") ||
    city.includes("la")
  ) {
    return "LA";
  }

  // New York
  if (
    city.includes("new york") ||
    city.includes("newyork") ||
    city.includes("nyc") ||
    region === "NY"
  ) {
    return "NYC";
  }

  // Other major cities
  if (city.includes("chicago")) return "CHI";
  if (city.includes("seattle")) return "SEA";
  if (city.includes("phoenix")) return "PHX";
  if (city.includes("denver")) return "DEN";
  if (city.includes("dallas")) return "DAL";
  if (city.includes("houston")) return "HOU";
  if (city.includes("philadelphia")) return "PHI";
  if (city.includes("portland")) return "PDX";
  if (city.includes("salt lake")) return "SLC";

  return null;
}

// Get city mapping from slug (case-insensitive)
export function getCityBySlug(slug: string): CityMapping | null {
  const upperSlug = slug.toUpperCase();
  return CITY_SLUG_MAP[upperSlug] || null;
}

// Get city slug from internal ID
export function getSlugFromInternalId(internalId: string): string | null {
  return INTERNAL_TO_SLUG[internalId] || null;
}
