package service

import (
	"context"
	"errors"
    "encoding/json"

	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/domain"
	"github.com/maher/stellapply/internal/infrastructure/external"
    "time"
)

type ResumeService struct {
	resumeRepo domain.ResumeRepository
	aiClient   *external.AIClient
}

func NewResumeService(rRepo domain.ResumeRepository, aiClient *external.AIClient) *ResumeService {
	return &ResumeService{
		resumeRepo: rRepo,
		aiClient:   aiClient,
	}
}

func (s *ResumeService) Analyze(ctx context.Context, id uuid.UUID) (*domain.Resume, error) {
    // 1. Get Resume
    resume, err := s.resumeRepo.GetByID(ctx, id)
    if err != nil {
        return nil, err
    }

    // 2. Call AI Service
    // Ensure content is stringified if it's JSON bytes
    contentStr := string(resume.Content)
    res, err := s.aiClient.AnalyzeResume(ctx, contentStr)
    if err != nil {
        return nil, err
    }

    // 3. Update Resume
    score := int32(res.AtsScore)
    now := time.Now()
    
    // Marshal analysis results to JSONBytes
    resultsBytes, _ := json.Marshal(res.AnalysisResults)

    resume.AtsScore = &score
    resume.AnalysisResults = resultsBytes
    resume.AnalyzedAt = &now

    if err := s.resumeRepo.Update(ctx, resume); err != nil {
        return nil, err
    }

    return resume, nil
}

func (s *ResumeService) Create(ctx context.Context, resume *domain.Resume) error {
	if resume.UserID == uuid.Nil {
		return errors.New("user_id is required")
	}
    if resume.Content == nil {
        resume.Content = []byte("{}")
    }

	// Check if this is the first resume, if so, make it primary
	existing, err := s.resumeRepo.ListByUserID(ctx, resume.UserID)
	if err == nil && len(existing) == 0 {
		resume.IsPrimary = true
	}

	return s.resumeRepo.Create(ctx, resume)
}

func (s *ResumeService) GetByID(ctx context.Context, id uuid.UUID) (*domain.Resume, error) {
	return s.resumeRepo.GetByID(ctx, id)
}

func (s *ResumeService) ListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Resume, error) {
	return s.resumeRepo.ListByUserID(ctx, userID)
}

func (s *ResumeService) Update(ctx context.Context, resume *domain.Resume) error {
    // If update requests IsPrimary=true, we should probably unset others (transactional usually).
    // For now, strict update on the single record.
    // Unset logic can be added later or client handles it.
	return s.resumeRepo.Update(ctx, resume)
}

func (s *ResumeService) Delete(ctx context.Context, id uuid.UUID) error {
	return s.resumeRepo.Delete(ctx, id)
}
