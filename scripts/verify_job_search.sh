#!/bin/bash
set -e

JOB_ID="b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
USER_ID="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

# 0. Cleanup
echo "Cleaning up..."
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "DELETE FROM job_matches WHERE job_id = '$JOB_ID';"
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "DELETE FROM jobs WHERE id = '$JOB_ID';"

# 1. Insert Dummy Job
echo "Inserting dummy job $JOB_ID..."
docker exec stellapply-postgres psql -U stellapply -d stellapply -c "
INSERT INTO jobs (id, title, company, url, description, status, raw_data, is_deleted) 
VALUES ('$JOB_ID', 'Senior Python Developer', 'StellarCorp', 'https://example.com/job', 'Looking for a Python/FastAPI expert.', 'active', '{}', false);
"

# 2. Test GET /api/v1/jobs/jobs (Expect 200)
echo "Testing GET /api/v1/jobs/jobs..."
curl -v -H "X-User-ID: $USER_ID" "http://localhost:8000/api/v1/jobs/jobs"
echo -e "\n"

# 3. Test POST /api/v1/jobs/jobs/{id}/match
echo "Testing Job Matching..."
curl -v -X POST -H "X-User-ID: $USER_ID" "http://localhost:8000/api/v1/jobs/jobs/$JOB_ID/match"
echo -e "\n"

# 4. Test GET /api/v1/jobs/matches
echo "Testing List Matches..."
curl -v -H "X-User-ID: $USER_ID" "http://localhost:8000/api/v1/jobs/matches"
echo -e "\n"
