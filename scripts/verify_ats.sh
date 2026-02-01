#!/bin/bash

# Configuration
API_URL="http://localhost:8080/api/v1"
USER_ID="b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22"

echo "Stellapply ATS Verification"
echo "==========================="

# Cleanup (ignore errors)
echo "Cleaning up..."
curl -s -X DELETE "$API_URL/resumes/cleanup" > /dev/null

# 0. Create User (Direct DB Injection for speed/consistency)
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "
INSERT INTO users (id, email_encrypted, email_hash, password_hash, status) 
VALUES ('$USER_ID', '\xDEADBEEF', 'hash_test_user_ats', 'pass_hash', 'active') 
ON CONFLICT (id) DO NOTHING;
"

echo "1. Create Resume..."
CREATE_RES=$(curl -s -X POST -H "Content-Type: application/json" -H "X-User-ID: $USER_ID" \
    -d '{
        "name": "ATS Test Resume",
        "template_id": "modern_v1",
        "content": {"personal_info": {"name": "Jane Doe", "summary": "Experienced engineer with Python, Go, and React skills."}}
    }' \
    "$API_URL/resumes")
echo "Response: $CREATE_RES"

RESUME_ID=$(echo $CREATE_RES | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Created Resume ID: $RESUME_ID"

echo -e "\n2. Trigger Analysis..."
ANALYZE_RES=$(curl -s -X POST -H "X-User-ID: $USER_ID" "$API_URL/resumes/$RESUME_ID/analyze")
echo "Analysis Response: $ANALYZE_RES"

# Check for score in response (simple grep)
if echo "$ANALYZE_RES" | grep -q '"ats_score":'; then
    echo -e "\n[SUCCESS] ATS Score found in response."
else
    echo -e "\n[FAILURE] ATS Score NOT found."
    exit 1
fi

echo -e "\n3. Verify Persistence (Get Resume)..."
GET_RES=$(curl -s -H "X-User-ID: $USER_ID" "$API_URL/resumes/$RESUME_ID")
echo "Get Response: $GET_RES"

if echo "$GET_RES" | grep -q '"analyzed_at":'; then
     echo -e "\n[SUCCESS] Analysis timestamp persisted."
else
     echo -e "\n[FAILURE] Analysis timestamp missing."
     exit 1
fi

echo -e "\nVerification Complete."
