# Generate Lob Campaign CSV

## Quick Start

Run the script to generate the CSV from your database:

```bash
# From project root
python backend/generate_lob_csv.py
```

This will create `lob_campaign_audience.csv` with all paid but unfulfilled appeals.

## Manual Database Query

If you need to generate the CSV manually from your database, use this SQL query:

```sql
SELECT 
    -- Recipient Address (Agency)
    CASE 
        WHEN i.citation_number LIKE '9%' THEN 'SFMTA Citation Review'
        WHEN i.citation_number LIKE 'SFPD%' THEN 'San Francisco Police Department - Traffic Division'
        WHEN i.citation_number LIKE 'SFSU%' THEN 'San Francisco State University - Parking & Transportation'
        ELSE 'SFMTA Citation Review'
    END as name,
    
    CASE 
        WHEN i.citation_number LIKE '9%' THEN '1 South Van Ness Avenue'
        WHEN i.citation_number LIKE 'SFPD%' THEN '850 Bryant Street'
        WHEN i.citation_number LIKE 'SFSU%' THEN '1600 Holloway Avenue'
        ELSE '1 South Van Ness Avenue'
    END as address_line1,
    
    CASE 
        WHEN i.citation_number LIKE '9%' THEN 'Floor 7'
        WHEN i.citation_number LIKE 'SFPD%' THEN 'Room 500'
        WHEN i.citation_number LIKE 'SFSU%' THEN 'Burk Hall 100'
        ELSE 'Floor 7'
    END as address_line2,
    
    'San Francisco' as address_city,
    'CA' as address_state,
    
    CASE 
        WHEN i.citation_number LIKE '9%' THEN '94103'
        WHEN i.citation_number LIKE 'SFPD%' THEN '94103'
        WHEN i.citation_number LIKE 'SFSU%' THEN '94132'
        ELSE '94103'
    END as address_zip,
    
    'US' as address_country,
    
    -- Appeal Data (Merge Variables)
    i.citation_number,
    p.appeal_type::text as appeal_type,
    d.draft_text as letter_text,
    
    -- Return Address (User)
    LEFT(i.user_name, 40) as user_name,
    LEFT(i.user_address_line1, 64) as user_address_line1,
    LEFT(COALESCE(i.user_address_line2, ''), 64) as user_address_line2,
    i.user_city as user_city,
    i.user_state as user_state,
    LPAD(i.user_zip::text, 5, '0') as user_zip,
    
    -- Additional Data
    COALESCE(i.violation_date, '') as violation_date,
    COALESCE(i.license_plate, '') as license_plate
    
FROM payments p
JOIN intakes i ON p.intake_id = i.id
JOIN drafts d ON d.intake_id = i.id 
    AND d.appeal_type = p.appeal_type
WHERE p.status = 'paid'
  AND p.is_fulfilled = false
  AND d.draft_text IS NOT NULL
  AND d.draft_text != ''
ORDER BY p.created_at DESC;
```

## CSV Column Descriptions

### Required Lob Columns

- **name** (max 40 chars): Recipient name (agency department)
- **address_line1** (max 64 chars): Primary address line
- **address_city** (max 200 chars): City name
- **address_state** (2-letter code): State abbreviation
- **address_zip** (ZIP or ZIP+4): Must preserve leading zeros

### Optional Lob Columns

- **address_line2** (max 64 chars): Secondary address line
- **address_country** (ISO code): Country code (US)

### Merge Variables (Appeal-Specific)

- **citation_number**: Parking citation number
- **appeal_type**: "standard" or "certified"
- **letter_text**: Full appeal letter text (will be merged into HTML template)
- **user_name**: User's name (for return address)
- **user_address_line1**: User's return address line 1
- **user_address_line2**: User's return address line 2 (optional)
- **user_city**: User's city
- **user_state**: User's state (2-letter code)
- **user_zip**: User's ZIP code
- **violation_date**: Date of violation (YYYY-MM-DD format)
- **license_plate**: Vehicle license plate number

## Notes

1. **ZIP Code Formatting**: Ensure ZIP codes preserve leading zeros (e.g., 07751, not 7751)
2. **Text Truncation**: Names and addresses are automatically truncated to Lob's limits
3. **Encoding**: CSV must be UTF-8 encoded
4. **Line Breaks**: Letter text uses `\n` for line breaks (will be processed by Lob)

## Using Docker Database

If your database is in Docker, you can run the script from within the container:

```bash
# Connect to API container
docker exec -it fightsftickets_api_1 python backend/generate_lob_csv.py

# Or run directly
docker exec -it fightsftickets_api_1 python -c "
import sys
sys.path.insert(0, '/app/backend')
from generate_lob_csv import generate_lob_csv
generate_lob_csv('/app/lob_campaign_audience.csv')
"
```

## Troubleshooting

### Database Connection Error
- Ensure database is running: `docker-compose ps db`
- Check DATABASE_URL in `.env` file
- Try connecting via Docker container instead

### Empty CSV
- Check if there are any paid but unfulfilled payments
- Verify drafts exist with draft_text
- Check payment status is 'paid' and is_fulfilled is false

### Encoding Issues
- Ensure CSV is saved as UTF-8
- Don't open in Excel and re-save (can corrupt encoding)
- Use a text editor that supports UTF-8

