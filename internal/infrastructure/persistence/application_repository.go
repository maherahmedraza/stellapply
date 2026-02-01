package persistence

import (
	"context"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/maher/stellapply/internal/domain"
)

type PostgresApplicationRepository struct {
	q *Queries
}

func NewPostgresApplicationRepository(q *Queries) *PostgresApplicationRepository {
	return &PostgresApplicationRepository{q: q}
}

func (r *PostgresApplicationRepository) Create(ctx context.Context, app *domain.Application) error {
	params := CreateApplicationParams{
		UserID:                  pgtype.UUID{Bytes: app.UserID, Valid: true},
		JobID:                   pgtype.UUID{Bytes: app.JobID, Valid: true},
		Status:                  pgtype.Text{String: app.Status, Valid: true},
		SubmissionMode:          pgtype.Text{String: app.SubmissionMode, Valid: true},
		SubmissionScreenshotUrl: pgtype.Text{String: app.SubmissionScreenshotUrl, Valid: true},
		ErrorMessage:            pgtype.Text{String: app.ErrorMessage, Valid: true},
		RetryCount:              pgtype.Int4{Int32: app.RetryCount, Valid: true},
		Timeline:                app.Timeline,
		ResumeSnapshot:          app.ResumeSnapshot,
		Answers:                 app.Answers,
	}

	if app.ResumeID != nil {
		params.ResumeID = pgtype.UUID{Bytes: *app.ResumeID, Valid: true}
	}
	if app.CoverLetterID != nil {
		params.CoverLetterID = pgtype.UUID{Bytes: *app.CoverLetterID, Valid: true}
	}
	if app.CoverLetterSnapshot != nil {
		params.CoverLetterSnapshot = pgtype.Text{String: *app.CoverLetterSnapshot, Valid: true}
	}
	if app.SubmittedAt != nil {
		params.SubmittedAt = pgtype.Timestamptz{Time: *app.SubmittedAt, Valid: true}
	}

	row, err := r.q.CreateApplication(ctx, params)
	if err != nil {
		return err
	}

	app.ID = row.ID.Bytes
	app.CreatedAt = row.CreatedAt.Time
	app.UpdatedAt = row.UpdatedAt.Time
	return nil
}

func (r *PostgresApplicationRepository) GetByID(ctx context.Context, id uuid.UUID) (*domain.Application, error) {
	row, err := r.q.GetApplicationByID(ctx, pgtype.UUID{Bytes: id, Valid: true})
	if err != nil {
		return nil, err
	}

	return r.mapToDomain(row), nil
}

func (r *PostgresApplicationRepository) ListByUserID(ctx context.Context, userID uuid.UUID) ([]*domain.Application, error) {
	rows, err := r.q.ListApplicationsByUserID(ctx, pgtype.UUID{Bytes: userID, Valid: true})
	if err != nil {
		return nil, err
	}

	apps := make([]*domain.Application, len(rows))
	for i, row := range rows {
		apps[i] = r.mapToDomain(row)
	}

	return apps, nil
}

func (r *PostgresApplicationRepository) Update(ctx context.Context, app *domain.Application) error {
	params := UpdateApplicationParams{
		ID:                      pgtype.UUID{Bytes: app.ID, Valid: true},
		Status:                  pgtype.Text{String: app.Status, Valid: true},
		SubmissionMode:          pgtype.Text{String: app.SubmissionMode, Valid: true},
		SubmissionScreenshotUrl: pgtype.Text{String: app.SubmissionScreenshotUrl, Valid: true},
		ErrorMessage:            pgtype.Text{String: app.ErrorMessage, Valid: true},
		RetryCount:              pgtype.Int4{Int32: app.RetryCount, Valid: true},
		Timeline:                app.Timeline,
		ResumeSnapshot:          app.ResumeSnapshot,
		Answers:                 app.Answers,
	}

	if app.ResumeID != nil {
		params.ResumeID = pgtype.UUID{Bytes: *app.ResumeID, Valid: true}
	}
	if app.CoverLetterID != nil {
		params.CoverLetterID = pgtype.UUID{Bytes: *app.CoverLetterID, Valid: true}
	}
	if app.CoverLetterSnapshot != nil {
		params.CoverLetterSnapshot = pgtype.Text{String: *app.CoverLetterSnapshot, Valid: true}
	}
	if app.SubmittedAt != nil {
		params.SubmittedAt = pgtype.Timestamptz{Time: *app.SubmittedAt, Valid: true}
	}

	row, err := r.q.UpdateApplication(ctx, params)
	if err != nil {
		return err
	}

	app.UpdatedAt = row.UpdatedAt.Time
	return nil
}

func (r *PostgresApplicationRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.q.DeleteApplication(ctx, pgtype.UUID{Bytes: id, Valid: true})
}

func (r *PostgresApplicationRepository) mapToDomain(row Application) *domain.Application {
	var resumeID *uuid.UUID
	if row.ResumeID.Valid {
		id := uuid.UUID(row.ResumeID.Bytes)
		resumeID = &id
	}

	var coverLetterID *uuid.UUID
	if row.CoverLetterID.Valid {
		id := uuid.UUID(row.CoverLetterID.Bytes)
		coverLetterID = &id
	}

	var coverLetterSnapshot *string
	if row.CoverLetterSnapshot.Valid {
		coverLetterSnapshot = &row.CoverLetterSnapshot.String
	}

	var submittedAt *time.Time
	if row.SubmittedAt.Valid {
		submittedAt = &row.SubmittedAt.Time
	}

	return &domain.Application{
		ID:                      row.ID.Bytes,
		UserID:                  row.UserID.Bytes,
		JobID:                   row.JobID.Bytes,
		ResumeID:                resumeID,
		ResumeSnapshot:          row.ResumeSnapshot,
		CoverLetterID:           coverLetterID,
		CoverLetterSnapshot:     coverLetterSnapshot,
		Answers:                 row.Answers,
		Status:                  row.Status.String,
		SubmissionMode:          row.SubmissionMode.String,
		SubmittedAt:             submittedAt,
		SubmissionScreenshotUrl: row.SubmissionScreenshotUrl.String,
		ErrorMessage:            row.ErrorMessage.String,
		RetryCount:              row.RetryCount.Int32,
		Timeline:                row.Timeline,
		CreatedAt:               row.CreatedAt.Time,
		UpdatedAt:               row.UpdatedAt.Time,
	}
}
