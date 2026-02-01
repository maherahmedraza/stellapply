#!/bin/bash
set -e

USER_ID="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
API_URL="http://localhost:8080/api/v1"

echo "Cleaning up..."
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "DELETE FROM resumes WHERE user_id = '$USER_ID';"
# Ensure user exists (Persona verify might have left it, but nice to be sure)
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "
INSERT INTO users (id, email_encrypted, email_hash, password_hash, status) 
VALUES ('$USER_ID', '\xDEADBEEF', 'hash_test_user_res', 'pass_hash', 'active') 
ON CONFLICT (id) DO NOTHING;
"

echo "1. Create Resume..."
CREATE_RES=$(curl -s -X POST -H "Content-Type: application/json" -H "X-User-ID: $USER_ID" \
    -d '{
        "name": "My First Resume",
        "template_id": "modern_v1",
        "content": {"personal_info": {"name": "John"}}
    }' \
    "$API_URL/resumes")
echo "Response: $CREATE_RES"

# Simple grep/sed extraction for ID (fragile but works without jq)
RESUME_ID=$(echo $CREATE_RES | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Created Resume ID: $RESUME_ID"

echo -e "\n2. List Resumes..."
curl -s -H "X-User-ID: $USER_ID" "$API_URL/resumes"

echo -e "\n3. Get Resume..."
curl -s -H "X-User-ID: $USER_ID" "$API_URL/resumes/$RESUME_ID"

echo -e "\n4. Update Resume..."
curl -s -X PUT -H "Content-Type: application/json" -H "X-User-ID: $USER_ID" \
     -d '{
        "name": "Updated Resume",
        "template_id": "modern_v2",
        "content": {"personal_info": {"name": "John Doe"}},
        "is_primary": true
     }' \
     "$API_URL/resumes/$RESUME_ID"

echo -e "\n5. Delete Resume..."
curl -v -X DELETE -H "X-User-ID: $USER_ID" "$API_URL/resumes/$RESUME_ID"
echo -e "\n"

echo "6. Verify Delete (Expect empty list or 404 on get)..."
curl -s -H "X-User-ID: $USER_ID" "$API_URL/resumes/$RESUME_ID"
