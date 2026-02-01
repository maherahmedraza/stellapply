package service

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/maher/stellapply/internal/domain"

	"github.com/google/uuid"
)

type PrivacyService struct {
	userRepo        domain.UserRepository
	personaRepo     domain.PersonaRepository
	resumeRepo      domain.ResumeRepository
	applicationRepo domain.ApplicationRepository
}

func NewPrivacyService(
	userRepo domain.UserRepository,
	personaRepo domain.PersonaRepository,
	resumeRepo domain.ResumeRepository,
	applicationRepo domain.ApplicationRepository,
) *PrivacyService {
	return &PrivacyService{
		userRepo:        userRepo,
		personaRepo:     personaRepo,
		resumeRepo:      resumeRepo,
		applicationRepo: applicationRepo,
	}
}

// ExportUserData aggregates all user data into a single JSON-serializable object (Right to Access)
func (s *PrivacyService) ExportUserData(ctx context.Context, userID uuid.UUID) ([]byte, error) {
	user, err := s.userRepo.GetByID(ctx, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	persona, _ := s.personaRepo.GetByUserID(ctx, userID)
	resumes, _ := s.resumeRepo.ListByUserID(ctx, userID)
	applications, _ := s.applicationRepo.ListByUserID(ctx, userID)

	exportData := map[string]interface{}{
		"user":         user,
		"persona":      persona,
		"resumes":      resumes,
		"applications": applications,
		"exported_at":  json.RawMessage(`"` + userID.String() + `"`), // Placeholder for timestamp
	}

	return json.MarshalIndent(exportData, "", "  ")
}

// DeleteUserAccount performs a cascading deletion of all user-related data (Right to Erasure)
func (s *PrivacyService) DeleteUserAccount(ctx context.Context, userID uuid.UUID) error {
	// In a real implementation, we would call repository methods to delete all related records
	// Here we assume the database has ON DELETE CASCADE configured (which it does in our schema)
	// So deleting the user record will trigger cascading deletion of personas, resumes, applications, etc.
	return s.userRepo.Delete(ctx, userID)
}

// RestrictProcessing effectively pauses AI automation for the user (Right to Restrict)
func (s *PrivacyService) RestrictProcessing(ctx context.Context, userID uuid.UUID, restricted bool) error {
	user, err := s.userRepo.GetByID(ctx, userID)
	if err != nil {
		return err
	}

	if restricted {
		user.Status = "restricted"
	} else {
		user.Status = "active"
	}

	return s.userRepo.Update(ctx, user)
}
