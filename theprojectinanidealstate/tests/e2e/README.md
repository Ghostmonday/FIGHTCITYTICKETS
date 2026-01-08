# E2E Testing: Full Route Coverage

Comprehensive end-to-end testing suite for FightCityTickets.com covering all routes, links, and user flows.

## Setup

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

## Running Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run only route coverage tests
npm run test:route-coverage

# View test report
npm run test:e2e:report
```

## Test Coverage

### ✅ Frontend Routes (18 routes)
- Home page
- Privacy & Terms
- All city pages (SF, LA, NYC, etc.)
- Case variations (uppercase/lowercase)

### ✅ Appeal Flow (5 routes)
- Appeal landing
- Camera step
- Review step
- Signature step
- Checkout step

### ✅ Navigation Links
- Footer links
- City navigation
- Appeal flow navigation

### ✅ API Endpoints (3+ routes)
- Health checks
- Citation validation
- Statement refinement

### ✅ User Flows
- Citation validation → Appeal
- Complete appeal journey
- State transitions

### ✅ Error Handling
- Invalid routes
- Missing parameters
- Broken links

## Configuration

Set environment variables:
```bash
BASE_URL=https://fightcitytickets.com  # Default
```

## Test Reports

Reports are generated in:
- HTML: `test-results/playwright-report/index.html`
- JSON: `test-results/e2e-results.json`

## Continuous Integration

Add to CI/CD pipeline:
```yaml
- name: Run E2E Tests
  run: |
    npm install
    npx playwright install --with-deps
    npm run test:e2e
```

---

*Full route coverage ensures no broken links or untested user paths.*

