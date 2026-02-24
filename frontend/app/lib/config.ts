/**
 * Application configuration
 * Uses environment variables for deployment flexibility
 */

export const config = {
  // Domain configuration
  domain: process.env.NEXT_PUBLIC_DOMAIN || "fightcitytickets.com",
  baseUrl:
    process.env.NEXT_PUBLIC_BASE_URL ||
    `https://${process.env.NEXT_PUBLIC_DOMAIN || "fightcitytickets.com"}`,

  // Support email
  supportEmail:
    process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@fightcitytickets.com",

  // API configuration
  apiBase:
    process.env.NEXT_PUBLIC_API_BASE ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000",

  // Analytics configuration
  googleAnalyticsId: process.env.NEXT_PUBLIC_GOOGLE_ANALYTICS_ID,
  mixpanelToken: process.env.NEXT_PUBLIC_MIXPANEL_TOKEN,
  amplitudeApiKey: process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY,
} as const;
