# Return Address Fix - Letter Body Inclusion

## Problem
Users' return addresses were only in the envelope header (top left), not clearly stated in the body of the appeal letter. If the envelope gets separated from the letter, the city wouldn't know where to send their response.

## Solution
Added explicit return address statement in the letter body, ensuring the city always knows where to send responses.

## Changes Made

### 1. **Mail Service - Letter Body Processing** (`backend/src/services/mail.py`)
- Added `_add_return_address_to_letter_body()` method
- Processes letter text before sending to:
  - Replace `[RETURN_ADDRESS]` placeholder with formatted user address
  - Replace `[Your Name]` and `[Your Address]` placeholders
  - Insert return address statement before closing if not already present
  - Format: "Please send your response regarding this appeal to the following address: [address]"

### 2. **PDF Generation** (`backend/src/services/mail.py`)
- Added return address section below signature in PDF
- Displays user's full address clearly
- Format: "Return Address: [name] [address] [city, state zip]"

### 3. **DeepSeek AI Prompt** (`backend/src/services/statement.py`)
- Updated prompt to instruct AI to include return address statement
- Uses `[RETURN_ADDRESS]` placeholder that gets replaced with actual address
- Ensures AI-generated letters include the return address request

### 4. **Fallback Letter Template** (`backend/src/services/statement.py`)
- Updated local fallback template to include return address statement
- Format: "Please send your response regarding this appeal to the following address: [RETURN_ADDRESS]"
- Placeholder gets replaced with actual user address

## Letter Format Example

```
[Date]

[Recipient Address]

Subject: Appeal of Citation #[number]

Dear Sir or Madam,

[Appeal content...]

I respectfully request that you review this matter and consider dismissing the citation.

Please send your response regarding this appeal to the following address:

John Doe
123 Main Street
San Francisco, CA 94102

Sincerely,

John Doe
```

## Benefits

1. **Clear Communication**: City always knows where to send responses
2. **Redundancy**: Address appears in both envelope header AND letter body
3. **Legal Protection**: Ensures users receive city responses even if envelope is lost
4. **Professional**: Standard business letter format

## Testing

To verify the fix works:
1. Create an appeal with user address
2. Check the generated letter text includes return address statement
3. Verify PDF includes return address below signature
4. Confirm address is formatted correctly

## Notes

- Return address is added automatically during mail processing
- Works with both AI-generated and fallback letters
- Address format: Name, Street, City, State ZIP
- Statement appears before closing (e.g., "Sincerely,")


