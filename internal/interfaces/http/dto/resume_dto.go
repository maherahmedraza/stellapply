package dto

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type CreateResumeRequest struct {
	Name       string          `json:"name"`
	TemplateID string          `json:"template_id"`
	Content    json.RawMessage `json:"content"`
	IsPrimary  bool            `json:"is_primary"`
}

type UpdateResumeRequest struct {
	Name       string          `json:"name"`
	TemplateID string          `json:"template_id"`
	Content    json.RawMessage `json:"content"`
	IsPrimary  bool            `json:"is_primary"`
}

type ResumeResponse struct {
	ID              uuid.UUID       `json:"id"`
	UserID          uuid.UUID       `json:"user_id"`
	Name            string          `json:"name"`
	TemplateID      string          `json:"template_id"`
	Content         json.RawMessage `json:"content"`
	PdfUrl          string          `json:"pdf_url,omitempty"`
	DocxUrl         string          `json:"docx_url,omitempty"`
	AtsScore        *int32          `json:"ats_score,omitempty"`
	AnalysisResults json.RawMessage `json:"analysis_results,omitempty"`
	AnalyzedAt      *time.Time      `json:"analyzed_at,omitempty"`
	IsPrimary       bool            `json:"is_primary"`
	Version         int32           `json:"version"`
	CreatedAt       time.Time       `json:"created_at"`
	UpdatedAt       time.Time       `json:"updated_at"`
}
