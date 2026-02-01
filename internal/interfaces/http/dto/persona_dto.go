package dto

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type PersonaRequest struct {
	PreferredName      string          `json:"preferred_name"`
	Pronouns           string          `json:"pronouns"`
	Location           json.RawMessage `json:"location"`
	WorkAuthorization  string          `json:"work_authorization"`
	Experience         json.RawMessage `json:"experience"`
	Education          json.RawMessage `json:"education"`
	Skills             json.RawMessage `json:"skills"`
	Certifications     json.RawMessage `json:"certifications"`
	Preferences        json.RawMessage `json:"preferences"`
	Personality        json.RawMessage `json:"personality"`
	BehavioralStories  json.RawMessage `json:"behavioral_stories"`
}

type PersonaResponse struct {
	ID                 uuid.UUID       `json:"id"`
	UserID             uuid.UUID       `json:"user_id"`
	PreferredName      string          `json:"preferred_name"`
	Pronouns           string          `json:"pronouns"`
	Location           json.RawMessage `json:"location"`
	WorkAuthorization  string          `json:"work_authorization"`
	Experience         json.RawMessage `json:"experience"`
	Education          json.RawMessage `json:"education"`
	Skills             json.RawMessage `json:"skills"`
	Certifications     json.RawMessage `json:"certifications"`
	Preferences        json.RawMessage `json:"preferences"`
	Personality        json.RawMessage `json:"personality"`
	BehavioralStories  json.RawMessage `json:"behavioral_stories"`
	CompletenessScore  int32           `json:"completeness_score"`
	CompletenessBreakdown json.RawMessage `json:"completeness_breakdown"`
	Version            int32           `json:"version"`
	CreatedAt          time.Time       `json:"created_at"`
	UpdatedAt          time.Time       `json:"updated_at"`
}
