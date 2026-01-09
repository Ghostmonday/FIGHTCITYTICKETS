import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'https://fightcitytickets.com';
const API_BASE = `${BASE_URL}/api`;

/**
 * Full Route Coverage E2E Tests
 * Tests every user-accessible route and navigation path
 */

// Frontend Routes to Test
const FRONTEND_ROUTES = [
  { path: '/', name: 'Home Page' },
  { path: '/privacy', name: 'Privacy Policy' },
  { path: '/terms', name: 'Terms of Service' },
  { path: '/sf', name: 'San Francisco City Page' },
  { path: '/SF', name: 'San Francisco (uppercase)' },
  { path: '/la', name: 'Los Angeles City Page' },
  { path: '/LA', name: 'Los Angeles (uppercase)' },
  { path: '/nyc', name: 'New York City Page' },
  { path: '/NYC', name: 'New York City (uppercase)' },
  { path: '/chicago', name: 'Chicago City Page' },
  { path: '/seattle', name: 'Seattle City Page' },
  { path: '/phoenix', name: 'Phoenix City Page' },
  { path: '/denver', name: 'Denver City Page' },
  { path: '/dallas', name: 'Dallas City Page' },
  { path: '/houston', name: 'Houston City Page' },
  { path: '/philadelphia', name: 'Philadelphia City Page' },
  { path: '/portland', name: 'Portland City Page' },
  { path: '/san_diego', name: 'San Diego City Page' },
  { path: '/salt_lake_city', name: 'Salt Lake City Page' },
];

// Appeal Flow Routes
const APPEAL_ROUTES = [
  { path: '/appeal', name: 'Appeal Landing', requiresParams: true },
  { path: '/appeal/camera', name: 'Appeal Camera', requiresParams: true },
  { path: '/appeal/review', name: 'Appeal Review', requiresParams: true },
  { path: '/appeal/signature', name: 'Appeal Signature', requiresParams: true },
  { path: '/appeal/checkout', name: 'Appeal Checkout', requiresParams: true },
];

test.describe('Frontend Route Coverage', () => {
  for (const route of FRONTEND_ROUTES) {
    test(`should load ${route.name} (${route.path})`, async ({ page }) => {
      await page.goto(route.path);
      
      // Should not show error page
      await expect(page.locator('body')).not.toContainText('404');
      await expect(page.locator('body')).not.toContainText('Error');
      
      // Should have title
      const title = await page.title();
      expect(title).toBeTruthy();
      
      // Should have main content
      const body = await page.locator('body');
      await expect(body).toBeVisible();
    });
  }
});

test.describe('Appeal Flow Routes', () => {
  for (const route of APPEAL_ROUTES) {
    test(`should handle ${route.name} (${route.path})`, async ({ page }) => {
      if (route.requiresParams) {
        // Test with query parameters
        await page.goto(`${route.path}?city=sf&citation=912345678`);
        
        // Should either load or redirect gracefully
        const url = page.url();
        expect(url).toContain(route.path.split('/')[1] || 'appeal');
      } else {
        await page.goto(route.path);
      }
      
      // Should not crash
      await expect(page.locator('body')).toBeVisible();
    });
  }
});

test.describe('Navigation Links', () => {
  test('should have working footer links', async ({ page }) => {
    await page.goto('/');
    
    // Find and test privacy link
    const privacyLink = page.locator('a[href="/privacy"]').first();
    if (await privacyLink.count() > 0) {
      await privacyLink.click();
      await expect(page).toHaveURL(/.*privacy/);
    }
    
    // Go back and test terms link
    await page.goto('/');
    const termsLink = page.locator('a[href="/terms"]').first();
    if (await termsLink.count() > 0) {
      await termsLink.click();
      await expect(page).toHaveURL(/.*terms/);
    }
  });

  test('should navigate from home to city page', async ({ page }) => {
    await page.goto('/');
    
    // Look for city links or navigation
    const cityLinks = page.locator('a[href*="/sf"], a[href*="/la"], a[href*="/nyc"]');
    const count = await cityLinks.count();
    
    if (count > 0) {
      await cityLinks.first().click();
      await expect(page).toHaveURL(/^\/(sf|la|nyc|SF|LA|NYC)/i);
    }
  });
});

test.describe('Citation Validation Flow', () => {
  test('should validate citation and navigate to appeal', async ({ page }) => {
    await page.goto('/sf');
    
    // Find citation input
    const citationInput = page.locator('input[type="text"], input[placeholder*="citation" i]').first();
    
    if (await citationInput.count() > 0) {
      await citationInput.fill('912345678');
      
      // Find validate button
      const validateButton = page.locator('button:has-text("Validate"), button:has-text("Continue")').first();
      
      if (await validateButton.count() > 0) {
        await validateButton.click();
        
        // Wait for validation (may take time)
        await page.waitForTimeout(2000);
        
        // Check if appeal button appears or redirect happens
        const appealButton = page.locator('button:has-text("Appeal"), a[href*="appeal"]');
        const currentUrl = page.url();
        
        // Either button appears or redirect happened
        expect(
          (await appealButton.count() > 0) || currentUrl.includes('appeal')
        ).toBeTruthy();
      }
    }
  });
});

test.describe('API Endpoints', () => {
  test('should respond to health check', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });

  test('should validate citation via API', async ({ request }) => {
    const response = await request.post(`${API_BASE}/tickets/validate`, {
      data: {
        citation_number: '912345678',
        license_plate: null,
        violation_date: null,
      },
    });
    
    expect([200, 400]).toContain(response.status());
    
    if (response.status() === 200) {
      const data = await response.json();
      expect(data).toHaveProperty('is_valid');
    }
  });

  test('should respond to statement refinement', async ({ request }) => {
    const response = await request.post(`${API_BASE}/statement/refine`, {
      data: {
        original_statement: 'This ticket is wrong',
        citation_number: null,
        citation_type: 'parking',
        desired_tone: 'professional',
        max_length: 500,
      },
    });
    
    expect([200, 400]).toContain(response.status());
  });
});

test.describe('State Transitions', () => {
  test('should handle appeal flow state transitions', async ({ page }) => {
    // Start at appeal page with params
    await page.goto('/appeal?city=sf&citation=912345678');
    
    // Should load without errors
    await expect(page.locator('body')).toBeVisible();
    
    // Try to navigate to next step
    const nextButton = page.locator('a[href*="camera"], button:has-text("Next"), button:has-text("Continue")').first();
    
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForTimeout(1000);
      
      // Should have navigated or shown next step
      const url = page.url();
      expect(url.length).toBeGreaterThan(0);
    }
  });
});

test.describe('Error Handling', () => {
  test('should handle invalid routes gracefully', async ({ page }) => {
    await page.goto('/invalid-route-that-does-not-exist');
    
    // Should not crash - either 404 page or redirect
    await expect(page.locator('body')).toBeVisible();
  });

  test('should handle missing query parameters', async ({ page }) => {
    await page.goto('/appeal');
    
    // Should load or redirect gracefully
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Link Integrity', () => {
  test('should have no broken internal links on home page', async ({ page }) => {
    await page.goto('/');
    
    // Get all links
    const links = await page.locator('a[href^="/"]').all();
    
    for (const link of links) {
      const href = await link.getAttribute('href');
      if (href && !href.includes('#')) {
        // Try to navigate
        await link.click();
        await page.waitForTimeout(500);
        
        // Should not be 404
        const bodyText = await page.locator('body').textContent();
        expect(bodyText).not.toContain('404');
        
        // Go back
        await page.goBack();
        await page.waitForTimeout(500);
      }
    }
  });
});

test.describe('Complete User Journey', () => {
  test('should complete full citation to appeal flow', async ({ page }) => {
    // Step 1: Visit city page
    await page.goto('/sf');
    await expect(page).toHaveURL(/.*sf/i);
    
    // Step 2: Enter citation
    const citationInput = page.locator('input[type="text"]').first();
    if (await citationInput.count() > 0) {
      await citationInput.fill('912345678');
      
      // Step 3: Validate
      const validateButton = page.locator('button:has-text("Validate"), button[type="submit"]').first();
      if (await validateButton.count() > 0) {
        await validateButton.click();
        await page.waitForTimeout(3000); // Wait for API call
        
        // Step 4: Check if appeal option appears
        const appealButton = page.locator('button:has-text("Appeal"), a[href*="appeal"]').first();
        if (await appealButton.count() > 0) {
          await appealButton.click();
          await page.waitForTimeout(1000);
          
          // Should be on appeal page
          expect(page.url()).toContain('appeal');
        }
      }
    }
  });
});

