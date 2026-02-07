import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Subdomain to city slug mapping
const SUBDOMAIN_TO_CITY: Record<string, string> = {
  sf: "SF",
  sanfrancisco: "SF",
  sd: "SD",
  sandiego: "SD",
  nyc: "NYC",
  newyork: "NYC",
  la: "LA",
  losangeles: "LA",
  sj: "SJ",
  sanjose: "SJ",
  chi: "CHI",
  chicago: "CHI",
  sea: "SEA",
  seattle: "SEA",
  phx: "PHX",
  phoenix: "PHX",
  den: "DEN",
  denver: "DEN",
  dal: "DAL",
  dallas: "DAL",
  hou: "HOU",
  houston: "HOU",
  phi: "PHI",
  philadelphia: "PHI",
  pdx: "PDX",
  portland: "PDX",
  slc: "SLC",
  saltlake: "SLC",
};

export function middleware(request: NextRequest) {
  const url = request.nextUrl.clone();
  const hostname = request.headers.get("host") || "";

  // Extract subdomain (e.g., "sf" from "sf.fightcitytickets.com")
  const subdomain = hostname.split(".")[0]?.toLowerCase();

  // Check if this is a subdomain request
  const isSubdomain =
    subdomain &&
    subdomain !== "www" &&
    subdomain !== "fightcitytickets" &&
    !hostname.includes("localhost") &&
    !hostname.includes("127.0.0.1");

  // If it's a subdomain, rewrite to city route
  if (isSubdomain && SUBDOMAIN_TO_CITY[subdomain]) {
    const citySlug = SUBDOMAIN_TO_CITY[subdomain];

    // If already on a city route, don't rewrite
    if (
      url.pathname.startsWith(`/${citySlug}`) ||
      url.pathname.startsWith("/appeal")
    ) {
      return NextResponse.next();
    }

    // Rewrite root to city page
    if (url.pathname === "/") {
      url.pathname = `/${citySlug}`;
      return NextResponse.rewrite(url);
    }

    // Rewrite other paths to include city context
    if (
      !url.pathname.startsWith("/api") &&
      !url.pathname.startsWith("/_next")
    ) {
      // Keep the path but ensure city context is available
      return NextResponse.next();
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
