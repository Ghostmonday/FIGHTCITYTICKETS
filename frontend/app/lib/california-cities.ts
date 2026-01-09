export interface CaliforniaCity {
  cityId: string;
  name: string;
  county: string;
  courtCode?: string;
}

export const CALIFORNIA_CITIES: CaliforniaCity[] = [
  {
    cityId: "us-ca-san_francisco",
    name: "San Francisco",
    county: "San Francisco",
    courtCode: "38",
  },
  {
    cityId: "us-ca-los_angeles",
    name: "Los Angeles",
    county: "Los Angeles",
    courtCode: "19",
  },
  {
    cityId: "us-ca-san_diego",
    name: "San Diego",
    county: "San Diego",
    courtCode: "37",
  },
  {
    cityId: "us-ca-oakland",
    name: "Oakland",
    county: "Alameda",
    courtCode: "1",
  },
  {
    cityId: "us-ca-sacramento",
    name: "Sacramento",
    county: "Sacramento",
    courtCode: "34",
  },
];

export function getCityById(cityId: string): CaliforniaCity | undefined {
  return CALIFORNIA_CITIES.find((city) => city.cityId === cityId);
}

export function getCityDisplayName(city: CaliforniaCity): string {
  return `${city.name}, ${city.county} County`;
}
