# FIGHTCITYTICKETS Architecture

## Overview
Automated parking ticket appeals platform that helps users contest citations through intelligent document preparation and submission.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIGHTCITYTICKETS Platform                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Frontend                               ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  ││
│  │  │  Landing    │ │  Case       │ │   Dashboard        │  ││
│  │  │  Page       │ │  Wizard     │ │   (User Portal)    │  ││
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      API Gateway                             ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  ││
│  │  │  Auth       │ │  Case       │ │   Document          │  ││
│  │  │  Routes     │ │  Routes     │ │   Routes            │  ││
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│  ┌───────────────────────────▼─────────────────────────────────┐│
│  │                    Core Services                             ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  ││
│  │  │  Appeal     │ │  Evidence   │ │   Jurisdiction      │  ││
│  │  │  Builder    │ │  Manager    │ │   Analyzer          │  ││
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  ││
│  │  ┌─────────────┐ ┌─────────────┐                            ││
│  │  │  PDF        │ │  Submit     │                            ││
│  │  │  Generator  │ │  Engine     │                            ││
│  │  └─────────────┘ └─────────────┘                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    External Integrations                    ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  ││
│  │  │  City Portal│ │  Email      │ │   Document         │  ││
│  │  │  API        │ │  Service    │ │   Storage           │  ││
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Appeal Builder
- Multi-step wizard for ticket info collection
- Grounds for appeal selection (valid reasons)
- Template system for common arguments
- Custom text input for unique circumstances

### 2. Evidence Manager
- Photo upload (timestamped)
- Document attachment
- Evidence categorization
- Supporting document templates

### 3. Jurisdiction Analyzer
- City-specific rules database
- Deadline calculators
- Fee structures by jurisdiction
- Appeal success rate by location

### 4. PDF Generator
- Auto-generated appeal letters
- Professional formatting
- Barcode/ticket reference inclusion
- Multi-page support

### 5. Submit Engine
- City portal integration
- Email submission fallback
- Proof of submission generation
- Deadline tracking

## Data Flow

1. **Intake**: User enters ticket info → Jurisdiction lookup → Deadlines calculated
2. **Build**: User selects grounds → Evidence upload → Appeal letter generated
3. **Review**: Preview PDF → User approval → Auto-format check
4. **Submit**: Submit to city portal/email → Confirmation received → Tracking started

## Technology Stack
- **Frontend**: React/Next.js (PWA)
- **Backend**: Node.js/Express or Python/FastAPI
- **Database**: PostgreSQL (case data)
- **Storage**: S3/Cloud storage (evidence files)
- **PDF**: PDFKit or similar
- **Email**: SendGrid/Postmark

## Features
- ✅ Multi-jisdiction support
- ✅ Automated deadline tracking
- ✅ Evidence photo timestamps
- ✅ PDF appeal generation
- ✅ Submission tracking
- ✅ Appeal history management

## Compliance
- Data privacy for personal info
- Secure evidence storage
- Court-ready document formatting
- Deadline reminder notifications
