package domain

import (
	"context"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type Persona struct {
	ID                 uuid.UUID
	UserID             uuid.UUID
	FullNameEncrypted  []byte
	PreferredName      string
	Pronouns           string
	Location           json.RawMessage // JSONB
	WorkAuthorization  string
	Experience         json.RawMessage // JSONB
	Education          json.RawMessage // JSONB
	Skills             json.RawMessage // JSONB
	Certifications     json.RawMessage // JSONB
	Preferences        json.RawMessage // JSONB
	Personality        json.RawMessage // JSONB
	BehavioralStories  json.RawMessage // JSONB
	CompletenessScore  int32
	CompletenessBreakdown json.RawMessage // JSONB
	Version            int32
	CreatedAt          time.Time
	UpdatedAt          time.Time
}

type PersonaRepository interface {
	Create(ctx context.Context, persona *Persona) error
	Update(ctx context.Context, persona *Persona) error
	GetByUserID(ctx context.Context, userID uuid.UUID) (*Persona, error)
}
