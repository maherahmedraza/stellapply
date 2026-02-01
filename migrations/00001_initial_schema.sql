-- +goose Up
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============ USERS & AUTH ============
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id UUID UNIQUE DEFAULT uuid_generate_v4(),
    email_encrypted BYTEA NOT NULL,
    email_hash VARCHAR(64) NOT NULL UNIQUE,
    phone_encrypted BYTEA,
    password_hash VARCHAR(255) NOT NULL,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret_encrypted BYTEA,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted', 'pending')),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'plus', 'pro', 'premium')),
    subscription_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    data_region VARCHAR(10) DEFAULT 'eu' CHECK (data_region IN ('eu', 'us', 'uk'))
);
CREATE INDEX idx_users_email_hash ON users(email_hash);
CREATE INDEX idx_users_status ON users(status) WHERE status = 'active';
CREATE INDEX idx_users_subscription ON users(subscription_tier);

-- ============ CONSENT MANAGEMENT ============
CREATE TABLE consent_purposes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO consent_purposes (id, name, description, required) VALUES
    ('essential', 'Essential Processing', 'Required for core service functionality', true),
    ('job_automation', 'Job Search Automation', 'Automated job searching and application submission', true),
    ('ai_generation', 'AI Document Generation', 'Using AI to generate resumes and cover letters', true),
    ('analytics', 'Analytics & Improvement', 'Help improve our services through usage analytics', false),
    ('marketing', 'Marketing Communications', 'Receive tips, updates, and promotional content', false),
    ('third_party', 'Third-Party Data Sharing', 'Share data with integrated services', false);

CREATE TABLE user_consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose_id VARCHAR(50) NOT NULL REFERENCES consent_purposes(id),
    granted BOOLEAN NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    withdrawn_at TIMESTAMPTZ,
    ip_address_hash VARCHAR(64),
    user_agent_hash VARCHAR(64),
    consent_version VARCHAR(10),
    UNIQUE(user_id, purpose_id)
);
CREATE INDEX idx_consents_user ON user_consents(user_id);

-- ============ PERSONAS ============
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name_encrypted BYTEA,
    preferred_name VARCHAR(100),
    pronouns VARCHAR(50),
    location JSONB,
    work_authorization VARCHAR(50),
    experience JSONB DEFAULT '[]',
    education JSONB DEFAULT '[]',
    skills JSONB DEFAULT '{}',
    certifications JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}',
    personality JSONB DEFAULT '{}',
    behavioral_stories JSONB DEFAULT '{}',
    summary_embedding vector(768),
    skills_embedding vector(768),
    completeness_score INTEGER DEFAULT 0,
    completeness_breakdown JSONB,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_personas_user ON personas(user_id);
-- CREATE INDEX IF NOT EXISTS idx_personas_embedding ON personas USING ivfflat (summary_embedding vector_cosine_ops);

-- ============ RESUMES ============
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    template_id VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    pdf_url VARCHAR(500),
    docx_url VARCHAR(500),
    ats_score INTEGER,
    analysis_results JSONB,
    analyzed_at TIMESTAMPTZ,
    is_primary BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resumes_primary ON resumes(user_id, is_primary) WHERE is_primary = TRUE;

-- ============ COVER LETTERS ============
CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID,
    resume_id UUID REFERENCES resumes(id),
    content TEXT NOT NULL,
    tone VARCHAR(20),
    length VARCHAR(20),
    emphasis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_cover_letters_user ON cover_letters(user_id);
CREATE INDEX idx_cover_letters_job ON cover_letters(job_id);

-- ============ JOBS ============
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(200) NOT NULL,
    source VARCHAR(50) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    company_logo_url VARCHAR(500),
    company_size VARCHAR(50),
    company_industry VARCHAR(100),
    title VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    requirements JSONB,
    nice_to_haves JSONB,
    location JSONB,
    is_remote BOOLEAN DEFAULT FALSE,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    apply_url VARCHAR(1000) NOT NULL,
    ats_platform VARCHAR(50),
    description_embedding vector(768),
    status VARCHAR(20) DEFAULT 'active',
    posted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(external_id, source)
);
CREATE INDEX idx_jobs_status ON jobs(status) WHERE status = 'active';
CREATE INDEX idx_jobs_posted ON jobs(posted_at DESC);
CREATE INDEX idx_jobs_location ON jobs USING gin(location);
-- CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs USING ivfflat (description_embedding vector_cosine_ops);
CREATE INDEX idx_jobs_search ON jobs USING gin(to_tsvector('english', title || ' ' || description));

-- ============ JOB MATCHES ============
CREATE TABLE job_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL,
    score_breakdown JSONB,
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'viewed', 'saved', 'hidden', 'applied')),
    matched_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ,
    UNIQUE(user_id, job_id)
);
CREATE INDEX idx_matches_user_status ON job_matches(user_id, status);
CREATE INDEX idx_matches_score ON job_matches(user_id, overall_score DESC);

-- ============ APPLICATIONS ============
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id),
    resume_id UUID REFERENCES resumes(id),
    resume_snapshot JSONB,
    cover_letter_id UUID REFERENCES cover_letters(id),
    cover_letter_snapshot TEXT,
    answers JSONB,
    status VARCHAR(30) DEFAULT 'pending',
    submission_mode VARCHAR(20),
    submitted_at TIMESTAMPTZ,
    submission_screenshot_url VARCHAR(500),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    timeline JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_submitted ON applications(submitted_at DESC);

-- ============ COMPANY BLACKLIST ============
CREATE TABLE company_blacklist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    company_name_normalized VARCHAR(200) NOT NULL,
    reason VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, company_name_normalized)
);
CREATE INDEX idx_blacklist_user ON company_blacklist(user_id);

-- ============ AUTOMATION SETTINGS ============
CREATE TABLE automation_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    mode VARCHAR(20) DEFAULT 'auto' CHECK (mode IN ('auto', 'review_first', 'manual')),
    daily_limit INTEGER DEFAULT 10,
    weekly_limit INTEGER DEFAULT 40,
    min_match_score INTEGER DEFAULT 60,
    active_hours JSONB,
    paused_until TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============ AUDIT LOG ============
CREATE TABLE audit_logs (
    id UUID DEFAULT uuid_generate_v4(),
    actor_id UUID,
    actor_type VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    ip_address_hash VARCHAR(64),
    user_agent_hash VARCHAR(64),
    old_values JSONB,
    new_values JSONB,
    metadata JSONB,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);

-- ============ RLS ============
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE personas ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE cover_letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_blacklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_consents ENABLE ROW LEVEL SECURITY;

-- +goose Down
DROP TABLE IF EXISTS audit_logs_2026_01;
DROP TABLE IF EXISTS audit_logs_2026_02;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS automation_settings;
DROP TABLE IF EXISTS company_blacklist;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS job_matches;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS cover_letters;
DROP TABLE IF EXISTS resumes;
DROP TABLE IF EXISTS personas;
DROP TABLE IF EXISTS user_consents;
DROP TABLE IF EXISTS consent_purposes;
DROP TABLE IF EXISTS users;
DROP EXTENSION IF EXISTS "pg_trgm";
DROP EXTENSION IF EXISTS "vector";
DROP EXTENSION IF EXISTS "pgcrypto";
DROP EXTENSION IF EXISTS "uuid-ossp";
