# Legacy vs Current Implementation Comparison

## 🔍 Key Differences Found

### Backend Framework
- **Legacy**: Flask (`backend_app.txt` shows Flask app)
- **Current**: FastAPI
- **Impact**: Different routing, middleware, and structure

### API Client Structure
- **Legacy**: Had complete typed API client (`api.txt`) with:
  - Proper TypeScript interfaces
  - Error handling for 202 Accepted responses
  - CheckoutData interface with `appeal_stage` and `mail_type`
- **Current**: No API client yet - needs to be created

### Frontend Components
- **Legacy**: Had `BackgroundAudio` component
- **Current**: Missing this component

### Data Models
- **Legacy**: Used `appeal_stage` ("initial" | "denovo") and `mail_type` ("regular" | "certified")
- **Current**: Uses `appeal_type` ("standard" | "certified")
- **Impact**: Field naming inconsistency

### Checkout Request Structure
**Legacy**:
```typescript
interface CheckoutData {
  citation_number: string;
  appeal_stage: "initial" | "denovo";
  mail_type: "regular" | "certified";
  // ... other fields
}
```

**Current**:
```typescript
// Uses appeal_type: "standard" | "certified"
// Missing appeal_stage concept
```

### Layout Structure
- **Legacy**: Had BackgroundAudio component, Plausible analytics, better metadata
- **Current**: Basic layout, missing analytics and background audio

### Voice Recorder
- **Legacy**: More sophisticated with audio level visualization, better error handling
- **Current**: Basic implementation, missing some features

---

## 🎯 Recommendations

### 1. Create API Client (High Priority)
Match the legacy structure with proper TypeScript types and error handling.

### 2. Add Missing Components
- BackgroundAudio component
- Better metadata in layout
- Analytics integration

### 3. Align Field Names
Consider if we need `appeal_stage` or if `appeal_type` is sufficient.

### 4. Enhance Voice Recorder
Add audio level visualization and better error handling from legacy.

---

## 📋 Action Items

1. ✅ Create typed API client matching legacy structure
2. ✅ Add BackgroundAudio component
3. ✅ Enhance layout with analytics
4. ✅ Improve voice recorder with visualization
5. ⚠️ Decide on appeal_stage vs appeal_type (may be intentional simplification)

