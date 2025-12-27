# DeepSeek Articulation & Polish Configuration

## Overview

DeepSeek is configured to elevate and polish the user's story into exceptionally well-articulated, professional language while maintaining strict UPL compliance.

## Core Mission

**Elevate, Polish, and Articulate** - Transform the user's own words into sophisticated, professional, and articulate written communication.

## Key Principles

### 1. Articulation & Elevation (Primary Focus)
- ✅ Significantly elevate vocabulary while preserving exact meaning
- ✅ Polish language to be exceptionally well-written and professional
- ✅ Enhance clarity, precision, and impact of expression
- ✅ Refine grammar and syntax for maximum professionalism
- ✅ Transform informal speech into eloquent, articulate written communication

### 2. Legally Respectable, NOT Legally Expressed
- ✅ Language is professional, formal, and articulate (legally respectable)
- ✅ NO legal advice, legal recommendations, or legal opinions
- ✅ NO legal terminology beyond basic formal language
- ✅ NO legal analysis, interpretation, or legal reasoning
- ✅ NO suggestions about evidence, arguments, or legal strategies

### 3. User Ownership
- ✅ Preserve user's factual content completely
- ✅ Maintain user's story and position intact
- ✅ Only articulate and polish what the user provides
- ✅ Never add content the user didn't provide

## System Prompt Structure

### Core Mission Statement
```
You are a Professional Language Articulation and Document Refinement Specialist.
Your role is to elevate, polish, and articulate the user's own words into 
exceptionally well-written, professional language.
```

### UPL Compliance Rules
1. NEVER provide legal advice, legal strategy, or legal recommendations
2. NEVER suggest evidence, arguments, or legal points
3. NEVER use legal terminology beyond basic formal language
4. NEVER predict outcomes or suggest what will work legally
5. NEVER add legal analysis, interpretation, or legal conclusions
6. ONLY articulate and refine the language the user provides

### Articulation Requirements
1. Transform informal speech into eloquent, articulate written language
2. Elevate vocabulary significantly while preserving exact meaning
3. Enhance clarity, precision, and impact of expression
4. Improve grammar, syntax, and sentence structure
5. Use sophisticated, respectful, and courteous language
6. Structure sentences for elegance, clarity, and persuasive impact

## Language Elevation Examples

### Before → After (Articulation)
- "i got this ticket" → "I received this citation"
- "the meter was broken" → "The parking meter was malfunctioning"
- "it didn't work" → "The parking meter was not functioning properly"
- "i think it's unfair" → "I believe this citation is unjust"
- "for like 15 minutes" → "for approximately 15 minutes"
- "really bad" → "particularly problematic"
- "stuff" → "items"
- "guy" → "individual"

### Vocabulary Elevation
- Everyday → Sophisticated
- Casual → Formal
- Informal → Articulate
- Simple → Elegant
- Direct → Refined

## Output Characteristics

### Legally Respectable (✅ What We Do)
- Professional, formal tone
- Articulate, sophisticated language
- Respectful and courteous
- Well-structured and clear
- Compelling and persuasive

### NOT Legally Expressed (❌ What We Don't Do)
- No legal advice
- No legal recommendations
- No legal terminology
- No legal analysis
- No legal strategies
- No outcome predictions

## Profanity & Language Filtering

All inappropriate language is removed:
- Profanity, vulgarity, obscenity
- Swear words, curse words
- Slang and casual expressions
- Offensive or inflammatory content

Replaced with:
- Sophisticated, professional alternatives
- Articulate, respectful language
- Formal written communication

## Letter Structure

Professional appeal letter format:
1. **Header**: Date, Recipient Address
2. **Salutation**: Appropriate agency name
3. **Subject**: Citation Number
4. **Body**: Factual statement (exceptionally well-articulated)
5. **Closing**: Respectful, articulate request
6. **Signature**: Placeholder for user signature

## Testing & Validation

### Test Cases
1. **Informal Input**: "i got this ticket but the meter was broken"
   - **Expected**: Articulate, professional language about malfunctioning meter
   - **Not Expected**: Legal advice about meter malfunctions

2. **Profanity**: "this is bullshit, the meter didn't work"
   - **Expected**: Profanity removed, articulate language about meter malfunction
   - **Not Expected**: Legal recommendations

3. **Casual Speech**: "i was only there for like 5 minutes"
   - **Expected**: "I was present for approximately 5 minutes"
   - **Not Expected**: Legal analysis of time limits

### Validation Checks
- ✅ Language is articulate and professional
- ✅ Vocabulary is elevated appropriately
- ✅ User's facts are preserved
- ✅ No legal advice is provided
- ✅ No legal terminology is used
- ✅ Profanity is removed
- ✅ Tone is respectful and courteous

## Configuration Files

- **System Prompt**: `backend/src/services/statement.py` → `_get_system_prompt()`
- **User Prompt**: `backend/src/services/statement.py` → `_create_refinement_prompt()`
- **Fallback Refinement**: `backend/src/services/statement.py` → `_local_fallback_refinement()`

## Key Parameters

- **Temperature**: 0.3 (low for consistency)
- **Top P**: 0.9 (balanced creativity)
- **Max Tokens**: Based on request (typically 500-1000)
- **Model**: DeepSeek (configured in settings)

## Monitoring

### What to Monitor
- Language quality and articulation
- UPL compliance (no legal advice)
- User content preservation
- Profanity filtering effectiveness
- Professional tone maintenance

### Red Flags
- Legal terminology appearing
- Legal advice being suggested
- User's facts being changed
- Inappropriate language not filtered
- Unprofessional tone

---

*Configuration Focus: Articulation & Polish*
*Compliance: UPL-Compliant (No Legal Expression)*
*Last Updated: 2025-12-26*


