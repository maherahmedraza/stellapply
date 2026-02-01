package dto

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type CreateApplicationRequest struct {
	JobID               uuid.UUID       `json:"job_id"`
	ResumeID            *uuid.UUID      `json:"resume_id"`
	ResumeSnapshot      json.RawMessage `json:"resume_snapshot"`
	CoverLetterID       *uuid.UUID      `json:"cover_letter_id"`
	CoverLetterSnapshot *string         `json:"cover_letter_snapshot"`
	Answers             json.RawMessage `json:"answers"`
	Status              string          `json:"status"`
	SubmissionMode      string          `json:"submission_mode"`
}

type UpdateApplicationRequest struct {
	ResumeID                *uuid.UUID      `json:"resume_id"`
	ResumeSnapshot          json.RawMessage `json:"resume_snapshot"`
	CoverLetterID           *uuid.UUID      `json:"cover_letter_id"`
	CoverLetterSnapshot     *string         `json:"cover_letter_snapshot"`
	Answers                 json.RawMessage `json:"answers"`
	Status                  string          `json:"status"`
	SubmissionMode          string          `json:"submission_mode"`
	SubmissionScreenshotUrl string          `json:"submission_screenshot_url"`
	ErrorMessage            string          `json:"error_message"`
	RetryCount              int32           `json:"retry_count"`
	Timeline                json.RawMessage `json:"timeline"`
}

type ApplicationResponse struct {
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
