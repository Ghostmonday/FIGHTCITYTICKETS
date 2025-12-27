#!/bin/bash
# Generate Lob CSV from database inside Docker container

echo "🔍 Generating Lob Campaign CSV from database..."
echo ""

# Run the generator inside the API container where database is accessible
docker exec -it fightsftickets_api_1 python backend/generate_lob_csv.py

# Copy the file out of the container if needed
if [ -f "lob_campaign_audience.csv" ]; then
    echo ""
    echo "✅ CSV file generated successfully!"
    echo "📄 Location: lob_campaign_audience.csv"
else
    echo ""
    echo "⚠️  CSV file not found. Check container logs for errors."
fi

