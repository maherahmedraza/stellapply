-- +goose Up
ALTER TABLE users ADD COLUMN governance_metadata JSONB DEFAULT '{
    "classification": "pii_standard",
    "retention_policy": "active_user",
    "legal_basis": "Article 6(1)(b) - Contract",
    "purpose": ["job_application_management"],
    "data_controller": "StellarApply GmbH",
    "processing_location": "EU",
    "third_party_sharing": false
}'::JSONB;

-- +goose Down
ALTER TABLE users DROP COLUMN IF EXISTS governance_metadata;
