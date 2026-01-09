# Lob Campaign Setup Guide

## Overview

This guide explains how to set up and use Lob Campaigns for bulk appeal letter mailing. The CSV file format follows Lob's Campaign Audience requirements.

## CSV File: `lob_campaign_audience.csv`

### Required Columns (Lob Standard)

1. **name** (max 40 chars)
   - Recipient name (appears in "To" field)
   - Example: "SFMTA Citation Review"

2. **address_line1** (max 64 chars)
   - Primary address line
   - Example: "1 South Van Ness Avenue"

3. **address_city** (max 200 chars)
   - City name
   - Example: "San Francisco"

4. **address_state** (2-letter code)
   - US state abbreviation
   - Example: "CA"

5. **address_zip** (ZIP or ZIP+4 format)
   - Must preserve leading zeros (e.g., 07751 not 7751)
   - Format: 12345 or 12345-1234
   - Example: "94103"

### Optional Columns (Lob Standard)

6. **address_line2** (max 64 chars)
   - Secondary address line (suite, floor, etc.)
   - Example: "Floor 7"

7. **address_country** (ISO 3166-1 alpha-2)
   - Country code
   - Example: "US"

8. **company** (max 40 chars)
   - Company name (if applicable)

### Merge Variables (Appeal-Specific)

These columns contain data that will be merged into your HTML template:

9. **citation_number**
   - The parking citation number being appealed
   - Example: "912345678"

10. **appeal_type**
    - Type of appeal: "standard" or "certified"
    - Example: "standard"

11. **letter_text**
    - The full appeal letter text (refined by DeepSeek AI)
    - This will be merged into your HTML template
    - Can contain multiple paragraphs separated by `\n\n`

12. **user_name**
    - Name of the person filing the appeal
    - Used for return address personalization
    - Example: "John Doe"

13. **user_address_line1**
    - User's return address line 1
    - Used for personalized return address
    - Example: "123 Main Street"

14. **user_address_line2** (optional)
    - User's return address line 2
    - Example: "Apt 4B"

15. **user_city**
    - User's city
    - Example: "San Francisco"

16. **user_state**
    - User's state (2-letter code)
    - Example: "CA"

17. **user_zip**
    - User's ZIP code
    - Example: "94102"

18. **violation_date** (optional)
    - Date of the violation
    - Format: YYYY-MM-DD
    - Example: "2024-01-15"

19. **license_plate** (optional)
    - Vehicle license plate number
    - Example: "ABC1234"

20. **city_id** (optional)
    - City identifier for multi-city support
    - Example: "us-ca-san_francisco"

21. **section_id** (optional)
    - Section identifier within the city
    - Example: "sfmta"

## CSV Formatting Requirements

### File Requirements
- **File extension:** `.csv`
- **Encoding:** UTF-8
- **Max size:** 5GB
- **First row:** Column headers (field names)

### Data Formatting Rules

1. **Whitespace:** Leading/trailing whitespace is automatically trimmed
2. **Commas:** Avoid commas in data values (use separate columns)
3. **Line breaks:** Avoid line breaks in CSV (use `\n` in merge variables if needed)
4. **ZIP codes:** Preserve leading zeros (e.g., 07751, not 7751)
5. **Special characters:** Use UTF-8 encoding for international characters

### Column Header Rules

Allowed characters in headers:
- Alphanumeric (a-z, A-Z, 0-9)
- Underscore (_)
- Dash (-)
- Parentheses (())
- Space ( )
- Period (.)

## Using the CSV in Lob Dashboard

### Step 1: Upload CSV
1. Go to Lob Dashboard > Campaigns
2. Create a new campaign
3. In Step 2: Add Audience, upload `lob_campaign_audience.csv`

### Step 2: Map Columns
Lob will auto-map columns that match their naming convention:
- `name` → Recipient name
- `address_line1` → Address line 1
- `address_city` → City
- `address_state` → State
- `address_zip` → ZIP code

Manually map merge variables:
- `citation_number` → Merge variable `{{citation_number}}`
- `appeal_type` → Merge variable `{{appeal_type}}`
- `letter_text` → Merge variable `{{letter_text}}`
- etc.

### Step 3: Configure Return Address

**Option A: Single Return Address**
- Use one return address for all recipients
- Set in Step 2 after uploading audience

**Option B: Personalized Return Address**
- Map return address fields:
  - `return_address_name` → `user_name`
  - `return_address_line1` → `user_address_line1`
  - `return_address_line2` → `user_address_line2`
  - `return_address_city` → `user_city`
  - `return_address_state` → `user_state`
  - `return_address_zip` → `user_zip`

### Step 4: Map Merge Variables
In Step 3: Choose Creative, map merge variables:
- `citation_number` → `{{citation_number}}`
- `appeal_type` → `{{appeal_type}}`
- `letter_text` → `{{letter_text}}`
- `user_name` → `{{user_name}}`
- `violation_date` → `{{violation_date}}` (if used)
- `license_plate` → `{{license_plate}}` (if used)

## Using the CSV with Lob API

### Upload Audience File

```python
POST /v1/uploads

{
   "campaignId": "{{campaign_id}}",
   "requiredAddressColumnMapping": {
       "name": "name",
       "address_line1": "address_line1",
       "address_zip": "address_zip",
       "address_state": "address_state",
       "address_city": "address_city"
   },
   "optionalAddressColumnMapping": {
       "address_line2": "address_line2",
       "address_country": "address_country"
   },
   "mergeVariableColumnMapping": {
       "citation_number": "citation_number",
       "appeal_type": "appeal_type",
       "letter_text": "letter_text",
       "user_name": "user_name",
       "violation_date": "violation_date",
       "license_plate": "license_plate"
   }
}
```

### Personalized Return Address Mapping

```python
{
   "returnAddressColumnMapping": {
       "return_address_name": "user_name",
       "return_address_line1": "user_address_line1",
       "return_address_line2": "user_address_line2",
       "return_address_city": "user_city",
       "return_address_state": "user_state",
       "return_address_zip": "user_zip"
   }
}
```

## Generating CSV from Database

To generate the CSV from your database, query the `payments` and `intakes` tables:

```sql
SELECT 
    -- Recipient address (agency)
    mail_address.name as name,
    mail_address.address1 as address_line1,
    mail_address.address2 as address_line2,
    mail_address.city as address_city,
    mail_address.state as address_state,
    mail_address.zip as address_zip,
    'US' as address_country,
    
    -- Appeal data (merge variables)
    i.citation_number,
    p.appeal_type,
    d.draft_text as letter_text,
    
    -- Return address (user)
    i.user_name as user_name,
    i.user_address_line1 as user_address_line1,
    i.user_address_line2 as user_address_line2,
    i.user_city as user_city,
    i.user_state as user_state,
    i.user_zip as user_zip,
    
    -- Additional data
    i.violation_date,
    i.license_plate,
    i.city_id,
    i.section_id
    
FROM payments p
JOIN intakes i ON p.intake_id = i.id
JOIN drafts d ON d.intake_id = i.id AND d.appeal_type = p.appeal_type
WHERE p.status = 'completed'
  AND p.is_fulfilled = false
  AND d.draft_text IS NOT NULL;
```

## Troubleshooting

### Common Issues

1. **ZIP codes missing leading zeros**
   - Excel/Google Sheets may strip leading zeros
   - Format ZIP column as text before exporting
   - Or use ZIP+4 format: `="07751"` in Excel

2. **CSV encoding errors**
   - Ensure file is UTF-8 encoded
   - Avoid opening in Excel and re-saving (can corrupt encoding)

3. **Merge variables not working**
   - Verify column names match exactly (case-sensitive)
   - Check that merge variable names in HTML template match column mappings

4. **Return address mapping errors**
   - Cannot use same column for recipient and return address
   - Ensure return address columns are separate from recipient columns

## Next Steps

1. **Populate CSV** with actual appeal data from your database
2. **Create HTML template** in Lob with merge variables
3. **Upload CSV** to Lob Dashboard or via API
4. **Map columns** to Lob fields and merge variables
5. **Configure return address** (single or personalized)
6. **Review proof** before sending
7. **Submit campaign** for processing

## Resources

- [Lob Campaigns Documentation](https://docs.lob.com/)
- [Campaign Audience Guide](https://docs.lob.com/campaigns/audience)
- [Merge Variables Guide](https://docs.lob.com/campaigns/merge-variables)

