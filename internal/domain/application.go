package domain

import (
	"context"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type Application struct {
	ID                      uuid.UUID       `json:"id"`
	UserID                  uuid.UUID       `json:"user_id"`
	JobID                   uuid.UUID       `json:"job_id"`
	ResumeID                *uuid.UUID      `json:"resume_id"`
	ResumeSnapshot          json.RawMessage `json:"resume_snapshot"`
	CoverLetterID           *uuid.UUID      `json:"cover_letter_id"`
	CoverLetterSnapshot     *string         `json:"cover_letter_snapshot"`
	Answers                 json.RawMessage `json:"answers"`
	Status                  string          `json:"status"`
	SubmissionMode          string          `json:"submission_mode"`
	SubmittedAt             *time.Time      `json:"submitted_at"`
	SubmissionScreenshotUrl string          `json:"submission_screenshot_url"`
	ErrorMessage            string          `json:"error_message"`
	RetryCount              int32           `json:"retry_count"`
	Timeline                json.RawMessage `json:"timeline"`
	CreatedAt               time.Time       `json:"created_at"`
	UpdatedAt               time.Time       `json:"updated_at"`
}

type ApplicationRepository interface {
	Create(ctx context.Context, app *Application) error
	GetByID(ctx context.Context, id uuid.UUID) (*Application, error)
	ListByUserID(ctx context.Context, userID uuid.UUID) ([]*Application, error)
	Update(ctx context.Context, app *Application) error
	Delete(ctx context.Context, id uuid.UUID) error
}
