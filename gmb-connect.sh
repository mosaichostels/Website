#!/bin/bash

# Google My Business Connection & Verification Script
# Project: Mosaic Hostel Varanasi
# Updated: 2026-07-04

PROJECT_ID="ai-seo-manager"
ACCOUNT_EMAIL="mosaichostels@gmail.com"
ACCOUNT_ID="accounts/188127158281998203"

echo "🔍 Google My Business Setup"
echo "=========================="
echo "Project: $PROJECT_ID"
echo "Account: $ACCOUNT_EMAIL"
echo "Account ID: $ACCOUNT_ID"
echo ""

# Step 1: Get Access Token
echo "Step 1: Getting access token..."
ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
echo "✓ Token obtained"
echo ""

# Step 2: Fetch Locations for Mosaic Hostel
echo "Step 2: Fetching locations for $ACCOUNT_ID..."
LOCATIONS=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://mybusinessbusinessinformation.googleapis.com/v1/$ACCOUNT_ID/locations")

echo "$LOCATIONS" | jq '.'

# Extract Location ID for Mosaic Hostel
LOCATION_ID=$(echo "$LOCATIONS" | jq -r '.locations[0].name' 2>/dev/null)

if [ -n "$LOCATION_ID" ] && [ "$LOCATION_ID" != "null" ]; then
  echo ""
  echo "✓ Location ID: $LOCATION_ID"
  echo ""
  echo "Step 3: Fetching location details..."
  curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    "https://mybusinessbusinessinformation.googleapis.com/v1/$LOCATION_ID" | jq '.'
else
  echo ""
  echo "Note: Could not extract location ID. Account ID may need adjustment."
fi
