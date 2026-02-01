package domain

import (
	"context"
	"time"

	"github.com/google/uuid"
)

type DataClassification string

const (
	PIICritical DataClassification = "pii_critical" // Encrypted + hashed, strict access
	PIIStandard DataClassification = "pii_standard" // Encrypted, logged access
	Sensitive   DataClassification = "sensitive"    // Encrypted, audit trail
	Internal    DataClassification = "internal"     // Standard protection
	Public      DataClassification = "public"       // No restrictions
)

type RetentionPolicy string

const (
	ActiveUser          RetentionPolicy = "active_user" // Retained while account active
	PostDeletion30D     RetentionPolicy = "30_days"     // 30 days after account deletion
	PostDeletion90D     RetentionPolicy = "90_days"     // 90 days (legal requirements)
	PermanentAnonymized RetentionPolicy = "permanent"   // Anonymized for analytics
)

type DataGovernanceMetadata struct {
	Classification      DataClassification `json:"classification"`
	RetentionPolicy     RetentionPolicy    `json:"retention_policy"`
	LegalBasis          string             `json:"legal_basis"` // GDPR Article 6 basis
	Purpose             []string           `json:"purpose"`
	DataController      string             `json:"data_controller"`
	ProcessingLocation  string             `json:"processing_location"`
	ThirdPartySharing   bool               `json:"third_party_sharing"`
	AnonymizationMethod *string            `json:"anonymization_method,omitempty"`
}

type User struct {
	ID                 uuid.UUID
	ExternalID         uuid.UUID
	EmailHash          string
	EmailEncrypted     []byte
	PasswordHash       string
	Status             string
	GovernanceMetadata DataGovernanceMetadata
	CreatedAt          time.Time
	UpdatedAt          time.Time
}

type UserRepository interface {
	Create(ctx context.Context, user *User) error
	GetByEmailHash(ctx context.Context, emailHash string) (*User, error)
	GetByID(ctx context.Context, id uuid.UUID) (*User, error)
	Update(ctx context.Context, user *User) error
	Delete(ctx context.Context, id uuid.UUID) error
}
