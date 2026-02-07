# Frontend Design System & Improvement Plan

## Design System Specifications

### Colors
| Role | Color | Usage |
|------|-------|-------|
| **Primary** | `#DC2626` (red-600) | Primary CTAs, key accents, focus rings |
| **Heading/Primary Text** | `#111827` (gray-900) | Headings, primary text, important content |
| **Secondary Text** | `#6B7280` (gray-500) | Body text, labels, supporting content |
| **Page Background** | `#F9FAFB` (gray-50) | Main page backgrounds |
| **Success** | `#10B981` (emerald-500) | Success states, confirmations, validation |
| **Warning** | `#F59E0B` (amber-500) | Warning states, disclaimers |
| **Error** | `#DC2626` (red-600) | Error states, validation errors |
| **Border** | `#E5E7EB` (gray-200) | Borders, dividers |
| **Surface** | `#FFFFFF` (white) | Cards, inputs, modals |

### Typography
- **Font**: Inter (already configured)
- **Hierarchy**:
  - H1: 32-48px, font-weight 600, leading-tight
  - H2: 24-32px, font-weight 600, leading-snug
  - H3: 20-24px, font-weight 500, leading-normal
  - Body: 16px (1rem), font-weight 400, leading-relaxed
  - Small: 14px (0.875rem), for labels, captions
  - Tiny: 12px (0.75rem), for disclaimers, hints

### Spacing Scale
- xs: 4px (0.25rem)
- sm: 8px (0.5rem)
- md: 16px (1rem)
- lg: 24px (1.5rem)
- xl: 32px (2rem)
- 2xl: 48px (3rem)
- 3xl: 64px (4rem)

### Border Radius
- sm: 6px
- md: 8px
- lg: 12px
- xl: 16px

### Shadows
- subtle: `0 1px 2px rgba(0, 0, 0, 0.05)`
- soft: `0 4px 6px -1px rgba(0, 0, 0, 0.05)`
- medium: `0 10px 15px -3px rgba(0, 0, 0, 0.08)`

### Animations
- fade-in: `animation: fadeIn 0.3s ease-out`
- slide-up: `animation: slideUp 0.4s ease-out`
- gentle-hover: `transition: all 0.2s ease`

---

## Page-by-Page Improvements

### 1. Home Page (`/`)
**Current Issues:**
- Overly dramatic hero copy ("They Demand Perfection")
- Stone-800 buttons instead of red (#DC2626)
- Long blocks of text
- Cluttered trust badges

**Improvements:**
```
Hero Section:
- Headline: "Got a parking ticket? We help you prepare your appeal."
- Subcopy: "Submit professionally formatted appeal documents in minutes."
- CTA: Red (#DC2626) button "Start Your Appeal"
- Disclaimer (small, gray): "Document preparation only — not legal advice"

Main Content:
- Simplified 3-step process (Validate → Upload → Submit)
- Clean city selection cards
- Compact UPL disclaimer
- No "Clerical Engine" jargon
```

### 2. City Selection (`/[city]` or new route)
**Current Issues:**
- Cities embedded in home page form
- No clear visual cards
- Blocked states (TX, NC, NJ, WA) not called out

**Improvements:**
```
- Cities displayed as clean, tappable cards
- Each card shows: City name, deadline days
- Blocked states have visual callout with explanation
- Compact "document prep only" note under each
- Smooth navigation to intake flow
```

### 3. Appeal Intake (`/appeal`)
**Current Issues:**
- Multi-step flow disconnected
- Citation and vehicle sections separate
- Labels and validation could be clearer

**Improvements:**
```
Unified Intake Flow:
- Single form combining citation + vehicle info
- Clear inline validation messages
- Photo upload as integrated step, not separate page
- Progress indicator at top
- Minimum 44px touch targets
```

### 4. Camera/Upload (`/appeal/camera`)
**Current Issues:**
- Upload zone not obvious
- No type/size hints
- OCR results take over the page

**Improvements:**
```
Photo Upload:
- Large dashed upload zone with icon
- Clear hints: "2-5 photos, JPG or PNG, max 10MB each"
- Take photo / Upload from library buttons side-by-side
- Photo preview grid with easy remove
- OCR detection shown subtly, not disruptive
```

### 5. Review (`/appeal/review`)
**Current Issues:**
- Dense text area
- "Clerical Engine" jargon
- AI refinement not prominent

**Improvements:**
```
Review Section:
- Scannable summary of entered info (citation, city, photos)
- Large statement textarea with character count
- "Refine with AI" button prominent but optional
- Clear next step: Signature
```

### 6. Signature (`/appeal/signature`)
**Current Issues:**
- Canvas not clearly marked "sign here"
- Mobile touch interaction could be better
- Mix of blue and gray buttons

**Improvements:**
```
Signature:
- Clear "Sign below" instruction
- Touch-friendly canvas (minimum 100px height)
- Large "Clear" and "Done" buttons (44px+)
- Live signature preview
- Back button clearly visible
```

### 7. Checkout (`/appeal/checkout`)
**Current Issues:**
- Price not the hero
- "Procedural Submission Summary" too verbose
- CTA label confusing

**Improvements:**
```
Checkout:
- Price ($39) prominently displayed top-right
- Address form clean and organized
- Full UPL disclaimer in clear box
- Single checkbox: "I understand this is document preparation only"
- CTA: "Proceed to Payment" (red button)
```

### 8. Success (`/success`)
**Current Issues:**
- Clerical ID buried in details
- Too much text
- Institutional tone

**Improvements:**
```
Success:
- Clerical ID (e.g., ND-XXXX-XXXX) as hero element
- Short: "Appeal submitted! Your tracking ID is above."
- 2-3 bullet points for next steps
- Support link for questions
```

### 9. Status Lookup (`/appeal/status`)
**Current Issues:**
- Gradient backgrounds
- Status colors inconsistent
- Emoji usage (not professional)

**Improvements:**
```
Status:
- Simple form: email + citation
- Clean status badges (paid/mailed/pending)
- Tracking number when available
- Professional icons (SVG), no emojis
- Clear empty and error states
```

---

## Component Standards

### Buttons
```
Primary:
- Background: #DC2626
- Text: White
- Padding: 12px 24px
- Border radius: 8px
- Hover: #B91C1C (slightly darker)
- Focus ring: #DC2626 (2px offset)

Secondary/Ghost:
- Background: Transparent
- Border: 1px solid #E5E7EB
- Text: #374151
- Hover: Background #F9FAFB

Disabled:
- Background: #E5E7EB
- Text: #9CA3AF
- Cursor: not-allowed
```

### Forms
```
Inputs:
- Height: 48px (touch-friendly)
- Border: 1px solid #E5E7EB
- Border radius: 8px
- Focus ring: 2px #DC2626
- Padding: 12px 16px
- Font size: 16px (prevents zoom on iOS)

Labels:
- Font size: 14px
- Font weight: 500
- Color: #374151
- Margin bottom: 6px

Validation:
- Success: Green border, check icon
- Error: Red border, error message below
- Error message: #DC2626, 14px
```

### Cards
```
- Background: #FFFFFF
- Border: 1px solid #E5E7EB
- Border radius: 12px
- Padding: 24px
- Shadow: subtle (for elevation)
```

### Alerts
```
Success:
- Background: #ECFDF5
- Border: 1px solid #10B981
- Icon: Green check
- Text: #065F46

Error:
- Background: #FEF2F2
- Border: 1px solid #DC2626
- Icon: Red X
- Text: #991B1B

Warning:
- Background: #FFFBEB
- Border: 1px solid #F59E0B
- Icon: Amber exclamation
- Text: #92400E
```

---

## UPL Compliance Guidelines

### Short Disclaimer (Home, Key Steps)
> "Document preparation only — not legal advice"

### Full Disclaimer (Checkout, Success)
> "FIGHTCITYTICKETS.com is a document preparation service. We help you create appeal paperwork but don't provide legal advice. Outcome determined by municipal authority."

### Forbidden Language
- ❌ "We will win your case"
- ❌ "Guaranteed dismissal"
- ❌ "Legal representation"
- ❌ "Lawyers"

### Required Language
- ✅ "Prepare your appeal"
- ✅ "Document preparation"
- ✅ "Submit paperwork"
- ✅ "Professional formatting"

---

## Mobile Requirements

### Touch Targets
- Minimum: 44×44px
- Buttons: 48×48px preferred
- Form inputs: 48px height

### Text Readability
- Body text: 16px minimum
- Headings: Scale appropriately
- No zoom triggers (use 16px+ for inputs)

### Layout
- Single column on mobile
- Generous margins (16px minimum)
- Forms stack vertically
- CTAs full width on mobile

### Interactions
- Smooth scrolling
- Clear focus states
- No hover-dependent interactions

---

## File Changes Summary

### New Files to Create
1. `frontend/components/ui/Button.tsx` - Reusable button component
2. `frontend/components/ui/Input.tsx` - Reusable input with validation
3. `frontend/components/ui/Select.tsx` - Reusable select component
4. `frontend/components/ui/Card.tsx` - Reusable card wrapper
5. `frontend/components/ui/Alert.tsx` - Success/error/warning alerts
6. `frontend/components/ui/Toast.tsx` - Toast notifications
7. `frontend/lib/design-system.ts` - Design system constants

### Files to Modify
1. `frontend/tailwind.config.js` - Add design system colors
2. `frontend/app/globals.css` - Add animation utilities
3. `frontend/app/page.tsx` - Home page redesign
4. `frontend/app/appeal/page.tsx` - Appeal flow redesign
5. `frontend/app/appeal/camera/page.tsx` - Upload improvements
6. `frontend/app/appeal/review/page.tsx` - Review enhancements
7. `frontend/app/appeal/signature/page.tsx` - Signature improvements
8. `frontend/app/appeal/checkout/page.tsx` - Checkout redesign
9. `frontend/app/success/page.tsx` - Success redesign
10. `frontend/app/appeal/status/page.tsx` - Status redesign
11. `frontend/components/FooterDisclaimer.tsx` - UPL updates
12. `frontend/components/LegalDisclaimer.tsx` - Consistent variants
