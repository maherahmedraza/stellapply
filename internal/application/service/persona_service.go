package service

import (
	"context"
	"errors"

	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/domain"
)

type PersonaService struct {
	personaRepo domain.PersonaRepository
	userRepo    domain.UserRepository
}

func NewPersonaService(pRepo domain.PersonaRepository, uRepo domain.UserRepository) *PersonaService {
	return &PersonaService{
		personaRepo: pRepo,
		userRepo:    uRepo,
	}
}

func (s *PersonaService) GetByUserID(ctx context.Context, userID uuid.UUID) (*domain.Persona, error) {
	persona, err := s.personaRepo.GetByUserID(ctx, userID)
	if err != nil {
		return nil, err
	}
	return persona, nil
}

func (s *PersonaService) Update(ctx context.Context, persona *domain.Persona) error {
    if persona.UserID == uuid.Nil {
        return errors.New("user_id is required")
    }
    
    // Check if exists
    existing, err := s.personaRepo.GetByUserID(ctx, persona.UserID)
    if err != nil {
        // Simple check for "no rows" error string from pgx
        if err.Error() == "no rows in result set" {
             return s.personaRepo.Create(ctx, persona)
        }
        // If other error (e.g. scan error), return it
        return err
    }
    
    // Update existing ID
    persona.ID = existing.ID
    return s.personaRepo.Update(ctx, persona)
}
