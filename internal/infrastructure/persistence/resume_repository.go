package persistence

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/maher/stellapply/internal/domain"
)

type PostgresResumeRepository struct {
	q *Queries
}

func NewPostgresResumeRepository(q *Queries) *PostgresResumeRepository {
	return &PostgresResumeRepository{q: q}
}

func (r *PostgresResumeRepository) Create(ctx context.Context, res *domain.Resume) error {
	params := CreateResumeParams{
		UserID:     pgtype.UUID{Bytes: res.UserID, Valid: true},
		Name:       res.Name,
		TemplateID: res.TemplateID,
		Content:    res.Content,
		IsPrimary:  pgtype.Bool{Bool: res.IsPrimary, Valid: true},
	}

	row, err := r.q.CreateResume(ctx, params)
	if err != nil {
		return err
	}

	res.ID = row.ID.Bytes
	res.CreatedAt = row.CreatedAt.Time
	res.UpdatedAt = row.UpdatedAt.Time
	res.Version = row.Version.Int32
	// Map other potentially generated fields back if needed
	return nil
}

func (r *PostgresResumeRepository) GetByID(ctx context.Context, id uuid.UUID) (*domain.Resume, error) {
	row, err := r.q.GetResumeByID(ctx, pgtype.UUID{Bytes: id, Valid: true})
	if err != nil {
		return nil, err
	}

	return r.mapToDomain(row), nil
}

func (r *PostgresResumeRepository) ListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Resume, error) {
	rows, err := r.q.ListResumesByUserID(ctx, pgtype.UUID{Bytes: userID, Valid: true})
	if err != nil {
		return nil, err
	}

	resumes := make([]*domain.Resume, len(rows))
	for i, row := range rows {
		resumes[i] = r.mapToDomain(row)
	}

	return resumes, nil
}

func (r *PostgresResumeRepository) Update(ctx context.Context, res *domain.Resume) error {
	var atsScore pgtype.Int4
	if res.AtsScore != nil {
		atsScore = pgtype.Int4{Int32: *res.AtsScore, Valid: true}
	}
	
	var analyzedAt pgtype.Timestamptz
	if res.AnalyzedAt != nil {
		analyzedAt = pgtype.Timestamptz{Time: *res.AnalyzedAt, Valid: true}
	}

	params := UpdateResumeParams{
		ID:              pgtype.UUID{Bytes: res.ID, Valid: true},
		Name:            res.Name,
		TemplateID:      res.TemplateID,
		Content:         res.Content,
		IsPrimary:       pgtype.Bool{Bool: res.IsPrimary, Valid: true},
		AtsScore:        atsScore,
		AnalysisResults: res.AnalysisResults,
		AnalyzedAt:      analyzedAt,
	}

	row, err := r.q.UpdateResume(ctx, params)
	if err != nil {
		return err
	}

	res.UpdatedAt = row.UpdatedAt.Time
	res.Version = row.Version.Int32
	return nil
}

func (r *PostgresResumeRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.q.DeleteResume(ctx, pgtype.UUID{Bytes: id, Valid: true})
}

func (r *PostgresResumeRepository) mapToDomain(row Resume) *domain.Resume {
	var atsScore *int32
	if row.AtsScore.Valid {
		atsScore = &row.AtsScore.Int32
	}

	var analyzedAt *time.Time
	if row.AnalyzedAt.Valid {
		analyzedAt = &row.AnalyzedAt.Time
	}

	return &domain.Resume{
		ID:              row.ID.Bytes,
		UserID:          row.UserID.Bytes,
		Name:            row.Name,
		TemplateID:      row.TemplateID,
		Content:         row.Content,
		PdfUrl:          row.PdfUrl.String,
		DocxUrl:         row.DocxUrl.String,
		AtsScore:        atsScore,
		AnalysisResults: row.AnalysisResults,
		AnalyzedAt:      analyzedAt,
		IsPrimary:       row.IsPrimary.Bool,
		Version:         row.Version.Int32,
		CreatedAt:       row.CreatedAt.Time,
		UpdatedAt:       row.UpdatedAt.Time,
	}
}
