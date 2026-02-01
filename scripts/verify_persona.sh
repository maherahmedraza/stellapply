#!/bin/bash
set -e

USER_ID="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

# 0. Cleanup
echo "Cleaning up..."
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "DELETE FROM personas WHERE user_id = '$USER_ID';"
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "DELETE FROM users WHERE id = '$USER_ID';"

# 1. Insert Dummy User
echo "Inserting dummy user $USER_ID..."
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "
INSERT INTO users (id, email_encrypted, email_hash, password_hash, status) 
VALUES ('$USER_ID', '\xDEADBEEF', 'hash_test_user', 'pass_hash', 'active');
"

# 2. Test GET (Expect 404)
echo "Testing GET /api/v1/persona (Expect 404)..."
curl -v -H "X-User-ID: $USER_ID" http://localhost:8080/api/v1/persona || true
echo -e "\n"

# 3. Test PUT (Create)
echo "Testing PUT /api/v1/persona..."
curl -v -X PUT -H "Content-Type: application/json" -H "X-User-ID: $USER_ID" \
    -d '{
        "preferred_name": "John Doe",
        "pronouns": "he/him",
        "location": {"city": "New York", "country": "USA"},
        "work_authorization": "US Citizen",
        "experience": [{"title": "Software Engineer", "company": "Tech Corp"}],
        "education": [{"degree": "BS CS", "school": "University"}]
    }' \
    http://localhost:8080/api/v1/persona
echo -e "\n"

# 4. Test GET (Expect 200)
echo "Testing GET /api/v1/persona (Expect 200)..."
curl -v -H "X-User-ID: $USER_ID" http://localhost:8080/api/v1/persona
echo -e "\n"
