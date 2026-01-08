# FightCityTickets.com E2E Compliance Audit Report
## Operation Civil Shield Alignment Audit

**Date:** 2025-01-09  
**Project Path:** `C:\Comapnyfiles\provethat.io\FightSFTickets_Starter_Kit`  
**Status:** REQUIRES UPDATES  
**Priority:** CRITICAL

---

## EXECUTIVE SUMMARY

After comprehensive end-to-end audit of the FightCityTickets.com production codebase, the following issues were identified regarding Operation Civil Shield brand positioning and regulatory compliance:

| Category | Files Affected | Priority | Status |
|----------|----------------|----------|--------|
| Brand Voice Non-Compliance | 12 files | CRITICAL | Pending |
| Missing "We aren't lawyers" Disclaimer | 8 files | CRITICAL | Pending |
| AI Statement System - User Voice Issues | 3 files | HIGH | Pending |
| Email Templates - Non-Compliant Language | 2 files | HIGH | Pending |
| SEO/Meta - Keywords to Exclude | 3 files | MEDIUM | Pending |
| Footer/Static Pages | 4 files | MEDIUM | Pending |

---

## PROJECT STRUCTURE

The complete production-ready project resides in:

```
C:\Comapnyfiles\provethat.io\FightSFTickets_Starter_Kit\
├── frontend\                          # Next.js 14 production frontend
│   ├── app\                           # App router pages
│   │   ├── page.tsx                   # Homepage (NEEDS UPDATE)
│   │   ├── terms\page.tsx             # Terms of Service (NEEDS UPDATE)
│   │   ├── privacy\page.tsx           # Privacy Policy
│   │   ├── success\page.tsx           # Success page (NEEDS UPDATE)
│   │   ├── refund\page.tsx            # Refund policy
│   │   ├── appeal\                    # Appeal flow (NEEDS UPDATE)
│   │   │   ├── page.tsx
│   │   │   ├── camera\page.tsx
│   │   │   ├── review\page.tsx
│   │   │   ├── checkout\page.tsx
│   │   │   └── signature\page.tsx
│   │   └── blog\page.tsx              # Blog (NEEDS UPDATE)
│   ├── components\                    # React components
│   │   ├── LegalDisclaimer.tsx        # (NEEDS UPDATE)
│   │   └── FooterDisclaimer.tsx       # (NEEDS UPDATE)
│   └── lib\                           # Utilities
├── backend\                           # FastAPI production backend
│   ├── src\                           # Source code
│   │   ├── routes\                    # API endpoints
│   │   │   ├── statement.py           # AI statement (NEEDS UPDATE)
│   │   │   ├── checkout.py
│   │   │   ├── tickets.py
│   │   │   ├── webhooks.py
│   │   │   └── status.py
│   │   └── services\                  # Business logic
│   │       ├── statement.py           # AI service (NEEDS UPDATE)
│   │       ├── mail.py                # Mailing service
│   │       └── email_service.py       # Email templates (NEEDS UPDATE)
│   └── alembic\                       # Database migrations
└── cities\                            # City configurations
```

---

## SECTION 1: CRITICAL - Brand Voice & Legal Compliance

### 1.1 Frontend Homepage (`frontend/app/page.tsx`)

**Issues Identified:**
- Hero section uses non-compliant messaging ("Don't Stress. Fight Your Ticket.")
- Missing "We aren't lawyers. We're paperwork experts." core statement
- CTA button promises outcomes ("Get My Ticket Dismissed")
- Sub-headline lacks procedural compliance positioning

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-001: REPLACE HERO SECTION
// Location: Lines 170-210
// Current: "Don't Stress. Fight Your Ticket." 
// Required: "They Demand Perfection. We Deliver It."

<h1 className="text-4xl sm:text-5xl md:text-6xl font-extralight mb-8 tracking-tight text-stone-800 leading-tight">
  They Demand Perfection.<br className="hidden sm:block" /> We Deliver It.
</h1>
<p className="text-xl sm:text-2xl mb-3 font-light text-stone-500 max-w-xl mx-auto tracking-wide">
  A parking citation is a procedural document.
</p>
<p className="text-lg sm:text-xl mb-10 text-stone-600 max-w-xl mx-auto">
  Municipalities win through clerical precision.<br className="hidden sm:block" />
  <span className="font-normal text-stone-700">We make their weapon our shield.</span>
</p>

// ADD after hero section:
<div className="mt-6 text-sm text-stone-500 font-medium">
  We aren't lawyers. We're paperwork experts. And in a bureaucracy, paperwork is power.
</div>

// TODO-CIVIL-SHIELD-002: REPLACE SUB-HEADLINE
<h2 className="text-2xl sm:text-3xl md:text-4xl font-extralight mb-4 tracking-tight text-stone-700">
  Due Process as a Service
</h2>
<p className="text-base sm:text-lg max-w-lg mx-auto font-light text-stone-500">
  We don't offer legal advice. We deliver procedural perfection—formatted exactly how the city requires it.
</p>

// TODO-CIVIL-SHIELD-004: REPLACE CTA BUTTON
// Location: ~Line 360
// Current: "Get My Ticket Dismissed →"
// Required: "Validate Citation →" or "Submit Appeal →"
```

### 1.2 Legal Disclaimer Component (`frontend/components/LegalDisclaimer.tsx`)

**Issues Identified:**
- Current disclaimer lacks "We aren't lawyers. We're paperwork experts." core statement
- Missing procedural compliance framing
- Doesn't emphasize user voice preservation

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-010: REPLACE ALL DISCLAIMER TEXT VARIANTS
// Location: Lines 15-85

const disclaimerText = {
  full: (
    <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
      <p>
        <strong className="text-gray-800">We aren't lawyers. We're paperwork experts.</strong>{" "}
        In a bureaucracy, paperwork is power. We help you articulate and refine 
        your own reasons for appealing a parking ticket. We act as a scribe, helping you express 
        what <strong className="text-gray-800">you</strong> tell us is your reason for appealing.
      </p>
      <p>
        FightCityTickets.com is a <strong>procedural compliance service</strong>. We do not provide 
        legal advice, legal representation, or legal recommendations. We do not interpret laws 
        or guarantee outcomes. We ensure your appeal meets the exacting clerical standards 
        that municipalities use to reject citizen submissions.
      </p>
      <p className="text-xs text-gray-500 italic border-t border-gray-200 pt-3">
        If you require legal advice, please consult with a licensed attorney.
      </p>
    </div>
  ),
  compact: (
    <p className="text-xs text-gray-500 leading-relaxed">
      <strong>We aren't lawyers. We're paperwork experts.</strong> We help you articulate your own 
      reasons for appealing. Our service is procedural compliance—not legal advice.{" "}
      <a href="/terms" className="text-gray-700 hover:text-gray-900 underline underline-offset-2">
        Terms
      </a>
    </p>
  ),
  inline: (
    <span className="text-xs text-gray-400 italic">
      Document preparation service. Not a law firm. Paperwork is power.
    </span>
  ),
  elegant: (
    <div className="space-y-2 text-sm text-gray-600 leading-relaxed">
      <p>
        <strong className="text-gray-800">We aren't lawyers. We're paperwork experts.</strong>{" "}
        FightCityTickets.com is a procedural compliance service that helps you articulate 
        your own reasons for appealing a parking ticket. We refine and format the information 
        you provide to create a perfectly compliant appeal letter.
      </p>
      <p className="text-xs text-gray-500 border-t border-gray-100 pt-2">
        We do not provide legal advice. For legal guidance, consult a licensed attorney.
      </p>
    </div>
  ),
};
```

### 1.3 Terms of Service Page (`frontend/app/terms/page.tsx`)

**Issues Identified:**
- Service description lacks "We aren't lawyers" opening
- Missing procedural compliance vs legal advice distinction
- Doesn't emphasize user voice preservation

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-020: REPLACE SERVICE DESCRIPTION SECTION
// Location: Lines 25-55

<div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-8">
  <h3 className="text-lg font-semibold text-gray-900 mb-4">
    Service Description
  </h3>
  <div className="space-y-4 text-sm text-gray-700 leading-relaxed">
    <p>
      <strong className="text-gray-900">We aren't lawyers. We're paperwork experts.</strong>{" "}
      FightCityTickets.com is a procedural compliance service. We help you articulate 
      and refine your own reasons for appealing a parking ticket. We act as a scribe, 
      helping you express what <strong className="text-gray-900">you</strong> tell us 
      is your reason for appealing. We make the appeal process frictionless so you are 
      not intimidated into paying a ticket you believe is unfair.
    </p>
    <p>
      <strong className="text-gray-900">Procedural compliance, not legal advice.</strong>{" "}
      We are not a law firm, and we are not attorneys, legal practitioners, or legal 
      professionals. We do not provide legal advice, legal representation, legal 
      recommendations, or legal guidance. We do not suggest legal strategies, interpret 
      laws, guarantee outcomes, or make representations about the success of your appeal.
    </p>
    <p>
      Our tools assist you in formatting and articulating your own appeal based on 
      the information <strong className="text-gray-900">you</strong> provide. We ensure 
      your submission meets the exacting clerical standards that municipalities require. 
      You are solely responsible for the content, accuracy, and submission of your appeal. 
      Using this Service does not create an attorney-client relationship.
    </p>
    <p className="text-xs text-gray-500 italic pt-2 border-t border-gray-200">
      If you require legal advice, please consult with a licensed attorney.
    </p>
  </div>
</div>
```

### 1.4 Footer Disclaimer (`frontend/components/FooterDisclaimer.tsx`)

**Issues Identified:**
- Footer lacks "We aren't lawyers" core statement
- Missing procedural compliance framing

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-030: REPLACE FOOTER DISCLAIMER TEXT
// Location: Lines 10-25

<p className="text-xs text-gray-500 text-center leading-relaxed max-w-4xl mx-auto mb-4">
  <strong className="text-gray-700">We aren't lawyers. We're paperwork experts.</strong>{" "}
  FightCityTickets.com is a procedural compliance service that helps you articulate 
  your own reasons for appealing a parking ticket. We refine and format the information 
  you provide to create a professional appeal letter. We do not provide legal advice. 
  The decision to appeal and the arguments presented are entirely yours.
</p>
```

### 1.5 Success Page (`frontend/app/success/page.tsx`)

**Issues Identified:**
- Header uses outcome-focused messaging
- "What Happens Next" section lacks procedural framing
- Missing Clerical Engine™ terminology

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-040: REPLACE HEADER SECTION
// Location: Lines 95-120

<h1 className="text-4xl font-extrabold text-gray-900 mb-3">
  Submission Successful
</h1>
<p className="text-xl text-gray-700 mb-2 font-semibold">
  Your appeal is being processed with procedural perfection
</p>
<p className="text-gray-600">
  We've received your payment and generated your appeal letter. It will be mailed 
  within 1-2 business days—formatted exactly how {formatCityName(state.cityId)} requires it.
</p>

// TODO-CIVIL-SHIELD-041: REPLACE "WHAT HAPPENS NEXT" SECTION
// Location: Lines 130-165

<div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-8 text-white">
  <h2 className="text-2xl font-bold mb-6">Your Appeal Journey</h2>
  <div className="space-y-4">
    <div className="flex items-start gap-4">
      <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">1</div>
      <div>
        <h3 className="font-bold text-lg mb-1">Clerical Perfection</h3>
        <p className="text-green-100">
          Your appeal letter has been formatted with precise compliance to {formatCityName(state.cityId)} standards.
        </p>
      </div>
    </div>
    <div className="flex items-start gap-4">
      <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">2</div>
      <div>
        <h3 className="font-bold text-lg mb-1">Submission in Progress</h3>
        <p className="text-green-100">
          Your appeal will be mailed via {formatAppealType(paymentData?.appeal_type || "standard")} within 1-2 business days.
        </p>
      </div>
    </div>
    <div className="flex items-start gap-4">
      <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">3</div>
      <div>
        <h3 className="font-bold text-lg mb-1">Due Process Complete</h3>
        <p className="text-green-100">
          If successful, you keep your money. No ticket to pay. Clean record. 
          The city followed their own rules—you won by making them follow them perfectly.
        </p>
      </div>
    </div>
  </div>
</div>
```

### 1.6 Appeal Flow Pages

**Files Affected:**
- `frontend/app/appeal/page.tsx`
- `frontend/app/appeal/camera/page.tsx`
- `frontend/app/appeal/review/page.tsx`
- `frontend/app/appeal/checkout/page.tsx`
- `frontend/app/appeal/signature/page.tsx`

**Issues Identified:**
- Headers lack procedural framing
- Checkout page uses outcome-focused CTA
- Missing Clerical Engine™ terminology

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-050: UPDATE APPEAL PAGE HEADERS

// frontend/app/appeal/page.tsx - Lines 60-75
<h1 className="text-2xl font-bold mb-2">
  Submitting to {formatCityName(state.cityId)}
</h1>
<p className="text-gray-700 mb-2 font-medium">
  Your appeal is being processed through the Clerical Engine™.
</p>

// frontend/app/appeal/checkout/page.tsx - Lines 155-165
<div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
  <p className="font-semibold mb-2 text-blue-900">
    Clerical Engine™ Processing
  </p>
  <p className="text-sm text-blue-800">
    Your appeal will be formatted, printed, and mailed with procedural perfection. 
    Payment confirms your commitment to due process.
  </p>
</div>

// CTA BUTTON - Line ~250
// Current: "Get My Ticket Dismissed →"
// Required: "Submit Appeal →"
```

---

## SECTION 2: HIGH - AI Statement System (User Voice Compliance)

### 2.1 Backend Statement Service (`backend/src/services/statement.py`)

**Issues Identified:**
- System prompt lacks explicit user voice preservation requirement
- May inadvertently add legal arguments or strategies
- Missing "refine and articulate" vs "create content" distinction

**Required Changes:**

```python
# TODO-CIVIL-SHIELD-060: REPLACE SYSTEM PROMPT WITH COMPLIANT VERSION
# Location: Line ~142 - _get_system_prompt()

def _get_system_prompt(self) -> str:
    """Get the UPL-compliant system prompt for DeepSeek."""
    return """You are a Professional Language Articulation and Document Refinement Specialist for FightCityTickets.com.

CRITICAL COMPLIANCE REQUIREMENT - USER VOICE PRESERVATION:
Your role is to REFINE and ARTICULATE, not to create or modify content. You must PRESERVE:
- The user's exact factual content and story
- The user's position and argument
- The user's chosen points and evidence
- The user's voice and perspective

You must NEVER:
- Add legal arguments, strategies, or recommendations
- Suggest evidence the user didn't provide
- Interpret laws or regulations
- Tell the user what they "should" argue
- Predict outcomes or suggest what will work

You must ALWAYS:
- Elevate vocabulary while preserving exact meaning
- Polish grammar and syntax for professionalism
- Remove profanity and inappropriate language
- Maintain the user's story and position completely intact
- Format as a proper formal letter

CORE MISSION:
Transform the user's own words into exceptionally well-written, professional language. 
You are a master of articulation and refinement - elevating informal, everyday language 
into eloquent, respectful, and articulate written communication.

CRITICAL UPL COMPLIANCE (MANDATORY - NEVER VIOLATE):
1. NEVER provide legal advice, legal strategy, legal recommendations, or legal opinions
2. NEVER suggest what evidence to include, what arguments to make, or what legal points to raise
3. NEVER use legal terminology beyond basic formal language (e.g., "respectfully request" is fine, "pursuant to statute" is NOT)
4. NEVER predict outcomes, suggest legal strategies, or imply what will or won't work legally
5. NEVER add legal analysis, legal interpretation, legal conclusions, or legal reasoning
6. NEVER tell the user what they "should" do legally, what they "must" include, or what legal approach to take
7. ONLY articulate and refine the language the user provides - preserve their facts, their story, their position
8. NEVER add legal content, legal citations, legal references, or legal frameworks

WHAT YOU EXCEL AT:
- Elevating vocabulary from everyday to sophisticated and articulate
- Polishing language to be exceptionally well-written and professional
- Refining grammar and syntax for maximum clarity and impact
- Transforming informal speech into articulate, formal written communication
- Making the user's story sound professional, respectful, and compelling
- Ensuring language is legally respectable (professional, formal, articulate)

WHAT YOU NEVER DO:
- Provide legal advice, legal recommendations, or legal opinions
- Suggest evidence, arguments, or legal strategies
- Add legal analysis, interpretation, or legal reasoning
- Predict outcomes or suggest what will work legally
- Use legal terminology or legal frameworks

INPUT: User's informal statement about their parking ticket situation (may contain casual language, profanity, or informal speech)
OUTPUT: An exceptionally well-articulated, professionally polished appeal letter with:
- All profanity and inappropriate language removed
- Vocabulary significantly elevated while preserving exact meaning
- Language polished to be sophisticated, articulate, and professional
- Grammar and syntax refined for maximum clarity and impact
- Proper formal letter structure
- User's factual content, story, and position completely preserved
- Legally respectable tone (professional, formal, articulate)
- NO legal advice, legal recommendations, or legal expression
"""
```

### 2.2 Backend Statement Route (`backend/src/routes/statement.py`)

**Required Changes:**

```python
# TODO-CIVIL-SHIELD-061: ADD USER VOICE DISCLAIMER TO DOCSTRING
# Location: Lines 1-20

"""
Statement Refinement Routes for FightCityTickets.com

Handles AI-powered appeal statement refinement using DeepSeek.

IMPORTANT: This service REFINES and ARTICULATES user-provided content.
We do NOT create legal arguments, suggest strategies, or provide legal advice.
The user's voice and position are preserved - we only polish expression.

UPL Compliance:
- No legal advice is provided
- No legal strategies are suggested  
- No outcomes are predicted
- User's exact content and position are preserved
"""
```

### 2.3 Email Service (`backend/src/services/email_service.py`)

**Issues Identified:**
- Email templates use outcome-focused language
- Missing procedural compliance framing
- Lacks "We aren't lawyers" disclaimer

**Required Changes:**

```python
# TODO-CIVIL-SHIELD-070: REPLACE PAYMENT CONFIRMATION EMAIL
# Location: Lines 40-70

async def send_payment_confirmation(
    self,
    email: str,
    citation_number: str,
    amount_paid: int,
    appeal_type: str,
    session_id: str,
) -> bool:
    """Send payment confirmation email."""
    try:
        amount = "${:.2f}".format(amount_paid / 100)
        
        subject = "Your appeal submission is being processed | FightCityTickets.com"
        
        body = """FIGHTCITYTICKETS.COM

Submission Confirmed

Your appeal letter is being prepared for mailing. 

WHAT HAPPENS NEXT:
1. Your letter will be printed and mailed within 1-2 business days
2. You'll receive a tracking number when it ships
3. The city will respond directly to you by mail

IMPORTANT: We are a document preparation service—not a law firm. 
We help you submit your own appeal. The outcome depends on the city.

Thank you for choosing procedural perfection.

--
FightCityTickets.com
We aren't lawyers. We're paperwork experts.
"""
        
        logger.info(f"Payment confirmation email to {email}: Citation {citation_number}, Amount {amount}")
        return True
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {e}")
        return False

# TODO-CIVIL-SHIELD-071: REPLACE APPEAL MAILED EMAIL
# Location: Lines 75-100

async def send_appeal_mailed(
    self,
    email: str,
    citation_number: str,
    tracking_number: str,
    expected_delivery: Optional[str] = None,
) -> bool:
    """Send appeal mailed confirmation email."""
    try:
        subject = "Your appeal is on its way | FightCityTickets.com"
        
        body = """FIGHTCITYTICKETS.COM

Appeal Letter Shipped

Your appeal has been mailed to the city.

TRACKING: {tracking_number}
EXPECTED DELIVERY: {expected_delivery or "3-5 business days"}

Next steps:
- Monitor the tracking number for delivery confirmation
- Wait for the city to respond (typically 2-4 weeks)
- Respond to any city correspondence directly

Remember: We help you submit your appeal. We do not provide legal advice 
or represent you in any legal matter.

--
FightCityTickets.com
We aren't lawyers. We're paperwork experts.
"""
        
        logger.info(f"Appeal mailed email to {email}: Citation {citation_number}, Tracking {tracking_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send appeal mailed email: {e}")
        return False
```

---

## SECTION 3: MEDIUM - SEO & Metadata

### 3.1 Frontend Layout Metadata (`frontend/app/layout.tsx`)

**Issues Identified:**
- Title and description lack procedural compliance framing
- Keywords include "legal" terms that should be excluded
- Structured data missing service type

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-080: UPDATE SEO METADATA
// Location: Lines 8-50

export const metadata: Metadata = {
  title: "FightCityTickets.com - Due Process as a Service",
  description:
    "We aren't lawyers. We're paperwork experts. FightCityTickets helps you submit a procedurally perfect parking ticket appeal. Document preparation and mailing service—not legal advice.",
  keywords:
    "parking ticket appeal, contest parking ticket, fight parking citation, appeal parking violation, document preparation service, procedural compliance, paperwork experts",
  // ... rest of metadata
};

// TODO-CIVIL-SHIELD-081: UPDATE STRUCTURED DATA
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Organization",
      name: "FightCityTickets.com",
      url: "https://fightcitytickets.com",
      logo: "https://fightcitytickets.com/logo.png",
      description: "Procedural compliance service for parking ticket appeals. Document preparation—not legal advice.",
      sameAs: [],
      "serviceType": "Document Preparation Service",
      "areaServed": "United States",
    }),
  }}
/>
```

### 3.2 Blog Page (`frontend/app/blog/page.tsx`)

**Required Changes:**

```typescript
// TODO-CIVIL-SHIELD-090: REPLACE CTA SECTION
// Location: Lines ~115-135

<div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 text-white text-center shadow-xl">
  <h2 className="text-3xl font-bold mb-4">
    Due Process Delivered
  </h2>
  <p className="text-xl text-green-100 mb-2 max-w-2xl mx-auto font-medium">
    Your appeal is being processed with procedural perfection.
  </p>
  <p className="text-lg text-green-50 mb-6 max-w-2xl mx-auto">
    We format your appeal exactly how the city requires it. 
    The outcome is up to the city—we ensure your submission is flawless.
  </p>
  <Link
    href="/"
    className="inline-block bg-white text-green-600 px-8 py-4 rounded-lg font-bold hover:bg-green-50 transition text-lg shadow-lg hover:shadow-xl"
  >
    Submit Your Appeal →
  </Link>
</div>
```

---

## SECTION 4: MEDIUM - Backend Mail Service

### 4.1 Mail Service PDF Generation (`backend/src/services/mail.py`)

**Issues Identified:**
- PDF footer uses legal terminology ("pursuant to Vehicle Code Section 40215")

**Required Changes:**

```python
# TODO-CIVIL-SHIELD-100: UPDATE PDF FOOTER LANGUAGE
# Location: Lines ~318-325

# Current: "This appeal is submitted pursuant to Vehicle Code Section 40215."
# Required:

story.append(
    Paragraph(
        "This appeal is submitted pursuant to the municipal appeal process. "
        "The appellant respectfully requests that the issuing agency review this matter "
        "in accordance with applicable procedures.",
        ParagraphStyle(
            "Footer", parent=styles["Normal"], fontSize=9, textColor="gray"
        ),
    )
)
```

---

## SECTION 5: NEW - What We Are / What We Are Not Page

### 5.1 Create New Page (`frontend/app/what-we-are/page.tsx`)

**Required: CREATE NEW FILE**

```typescript
import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

export const metadata = {
  title: "What We Are / What We Are Not | FightCityTickets.com",
  description: "We aren't lawyers. We're paperwork experts. Learn about our procedural compliance service for parking ticket appeals.",
};

export default function WhatWeArePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8">
          <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            WE AREN'T LAWYERS. WE'RE PAPERWORK EXPERTS.
          </h1>
          
          <p className="text-xl text-gray-700 mb-8 font-medium">
            And in a bureaucracy, paperwork is power.
          </p>

          {/* WHAT WE ARE */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-green-500 pb-2">
              WHAT WE ARE
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Procedural Compliance Service
                </h3>
                <p className="text-gray-700">
                  We help you navigate the complex procedural requirements of municipal appeal 
                  systems. Think of us as the difference between representing yourself in court 
                  (pro se) and having someone help you fill out the forms correctly.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Document Preparation Service
                </h3>
                <p className="text-gray-700">
                  We take what you tell us—the facts, the circumstances, your side of the story—
                  and we format it into a professional appeal letter that meets the exacting 
                  standards of the issuing agency.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  A Submission Service
                </h3>
                <p className="text-gray-700">
                  We print and mail your appeal letter via certified or standard mail, ensuring 
                  it reaches the proper department within your appeal deadline.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  The Clerical Engine™
                </h3>
                <p className="text-gray-700">
                  Our technology scans your citation for procedural defects—missing elements, 
                  misclassification, timing errors, or clerical flaws that can invalidate an 
                  otherwise valid citation.
                </p>
              </div>
            </div>
          </div>

          {/* WHAT WE ARE NOT */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b-2 border-red-500 pb-2">
              WHAT WE ARE NOT
            </h2>
            
            <div className="space-y-6">
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Are Not a Law Firm
                </h3>
                <p className="text-gray-700">
                  We do not employ attorneys. We do not provide legal representation. We do not 
                  create attorney-client relationships.
                </p>
              </div>
              
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Provide Legal Advice
                </h3>
                <p className="text-gray-700">
                  We do not interpret laws, regulations, or case law. We do not suggest legal 
                  strategies or evaluate the legal merits of your case.
                </p>
              </div>
              
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Guarantee Outcomes
                </h3>
                <p className="text-gray-700">
                  The decision to dismiss a parking ticket rests entirely with the issuing agency 
                  or an administrative judge. We cannot and do not promise that your appeal will 
                  be successful.
                </p>
              </div>
              
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <h3 className="text-lg font-semibold text-red-900 mb-2">
                  We Do Not Practice Law
                </h3>
                <p className="text-gray-700">
                  We operate strictly within the bounds of document preparation services. We help 
                  you express YOUR position—we do not tell you what position to take.
                </p>
              </div>
            </div>
          </div>

          {/* IMPORTANT DISTINCTION */}
          <div className="bg-gray-100 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              THE IMPORTANT DISTINCTION
            </h2>
            <p className="text-gray-700 mb-4">
              A parking ticket appeal is a procedural process, not a legal trial. The same 
              requirements that municipalities use to reject citizen appeals (missing forms, 
              wrong formatting, missed deadlines) can be used to challenge their citations.
            </p>
            <p className="text-gray-700">
              We help you meet those requirements with precision. That is not legal advice—it 
              is administrative compliance.
            </p>
            <p className="text-gray-700 mt-4 font-medium">
              If you need legal representation or legal advice, please consult with a licensed 
              attorney in your jurisdiction.
            </p>
          </div>

          <LegalDisclaimer variant="full" />
        </div>
      </div>
    </div>
  );
}
```

---

## IMPLEMENTATION PHASES

### Phase 1: CRITICAL (Must ship before launch)
| Task | File | Status |
|------|------|--------|
| TODO-CIVIL-SHIELD-001 | `frontend/app/page.tsx` | Pending |
| TODO-CIVIL-SHIELD-010 | `frontend/components/LegalDisclaimer.tsx` | Pending |
| TODO-CIVIL-SHIELD-020 | `frontend/app/terms/page.tsx` | Pending |
| TODO-CIVIL-SHIELD-030 | `frontend/components/FooterDisclaimer.tsx` | Pending |
| TODO-CIVIL-SHIELD-040 | `frontend/app/success/page.tsx` | Pending |
| TODO-CIVIL-SHIELD-050 | `frontend/app/appeal/*.tsx` (5 files) | Pending |
| TODO-CIVIL-SHIELD-060 | `backend/src/services/statement.py` | Pending |
| TODO-CIVIL-SHIELD-110 | `frontend/app/what-we-are/page.tsx` | Pending |

### Phase 2: HIGH (Before or at launch)
| Task | File | Status |
|------|------|--------|
| TODO-CIVIL-SHIELD-061 | `backend/src/routes/statement.py` | Pending |
| TODO-CIVIL-SHIELD-070 | `backend/src/services/email_service.py` | Pending |
| TODO-CIVIL-SHIELD-071 | `backend/src/services/email_service.py` | Pending |

### Phase 3: MEDIUM (Post-launch)
| Task | File | Status |
|------|------|--------|
| TODO-CIVIL-SHIELD-080 | `frontend/app/layout.tsx` | Pending |
| TODO-CIVIL-SHIELD-090 | `frontend/app/blog/page.tsx` | Pending |
| TODO-CIVIL-SHIELD-100 | `backend/src/services/mail.py` | Pending |

---

## BRAND TRANSFORMATION SUMMARY

| Element | Before | After |
|---------|--------|-------|
| **Hero** | "Don't Stress. Fight Your Ticket." | "They Demand Perfection. We Deliver It." |
| **Core Promise** | Helping you appeal | "If the city demands perfection, so can you." |
| **Brand Statement** | Implicit helpful service | "We aren't lawyers. We're paperwork experts." |
| **Value Prop** | Save $100 or more | Procedural perfection—formatted exactly how the city requires it |
| **Enemy** | The ticket | Bureaucratic opacity and procedural asymmetry |
| **Hero** | The helpful app | Procedural exactness and the Clerical Engine™ |
| **CTA** | "Get My Ticket Dismissed" | "Submit Appeal" / "Validate Citation" |
| **Tone** | Helpful, supportive | Confident, precise, anti-establishment but lawful |
| **Trust Signal** | Generic legal disclaimers | Radical transparency—admitting when cases cannot be won |
| **Technology** | Not mentioned | The Clerical Engine™—defect detection, procedural generation |
| **AI Role** | Creates appeals | Refines and articulates user's own words |

---

## FORBIDDEN vs SAFE LANGUAGE PATTERNS

### Forbidden Patterns (NEVER USE)
| Phrase | Why |
|--------|-----|
| "We represent you" | Implies attorney-client relationship |
| "We will