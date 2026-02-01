package service

import (
	"context"
	"errors"

	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/domain"
)

type ApplicationService struct {
	appRepo domain.ApplicationRepository
}

func NewApplicationService(r domain.ApplicationRepository) *ApplicationService {
	return &ApplicationService{
		appRepo: r,
	}
}

func (s *ApplicationService) Create(ctx context.Context, app *domain.Application) error {
	if app.UserID == uuid.Nil {
		return errors.New("user_id is required")
	}
	if app.JobID == uuid.Nil {
		return errors.New("job_id is required")
	}
	if app.Status == "" {
		app.Status = "pending"
	}
	return s.appRepo.Create(ctx, app)
}

func (s *ApplicationService) GetByID(ctx context.Context, id uuid.UUID) (*domain.Application, error) {
	return s.appRepo.GetByID(ctx, id)
}

func (s *ApplicationService) ListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Application, error) {
	return s.appRepo.ListByUserID(ctx, userID)
}

func (s *ApplicationService) Update(ctx context.Context, app *domain.Application) error {
	return s.appRepo.Update(ctx, app)
}

func (s *ApplicationService) Delete(ctx context.Context, id uuid.UUID) error {
	return s.appRepo.Delete(ctx, id)
}
