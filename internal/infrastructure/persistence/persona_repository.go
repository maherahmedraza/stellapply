package persistence

import (
	"context"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/maher/stellapply/internal/domain"
)

type PostgresPersonaRepository struct {
	q *Queries
}

func NewPostgresPersonaRepository(q *Queries) *PostgresPersonaRepository {
	return &PostgresPersonaRepository{q: q}
}

func (r *PostgresPersonaRepository) Create(ctx context.Context, p *domain.Persona) error {
	params := CreatePersonaParams{
		UserID:            pgtype.UUID{Bytes: p.UserID, Valid: true},
		FullNameEncrypted: p.FullNameEncrypted,
		PreferredName:     pgtype.Text{String: p.PreferredName, Valid: p.PreferredName != ""},
		Pronouns:          pgtype.Text{String: p.Pronouns, Valid: p.Pronouns != ""},
		Location:          p.Location,
		WorkAuthorization: pgtype.Text{String: p.WorkAuthorization, Valid: p.WorkAuthorization != ""},
		Experience:        p.Experience,
		Education:         p.Education,
		Skills:            p.Skills,
		Certifications:    p.Certifications,
		Preferences:       p.Preferences,
		Personality:       p.Personality,
		BehavioralStories: p.BehavioralStories,
		CompletenessScore: pgtype.Int4{Int32: p.CompletenessScore, Valid: true},
		CompletenessBreakdown: p.CompletenessBreakdown,
	}

	row, err := r.q.CreatePersona(ctx, params)
	if err != nil {
		return err
	}

	p.ID = row.ID.Bytes
	p.CreatedAt = row.CreatedAt.Time
	p.UpdatedAt = row.UpdatedAt.Time
	return nil
}

func (r *PostgresPersonaRepository) Update(ctx context.Context, p *domain.Persona) error {
	params := UpdatePersonaParams{
		UserID:            pgtype.UUID{Bytes: p.UserID, Valid: true},
		FullNameEncrypted: p.FullNameEncrypted,
		PreferredName:     pgtype.Text{String: p.PreferredName, Valid: true}, // Allow clearing? For now assume strict update
		Pronouns:          pgtype.Text{String: p.Pronouns, Valid: true},
		Location:          p.Location,
		WorkAuthorization: pgtype.Text{String: p.WorkAuthorization, Valid: true},
		Experience:        p.Experience,
		Education:         p.Education,
		Skills:            p.Skills,
		Certifications:    p.Certifications,
		Preferences:       p.Preferences,
		Personality:       p.Personality,
		BehavioralStories: p.BehavioralStories,
		CompletenessScore: pgtype.Int4{Int32: p.CompletenessScore, Valid: true},
		CompletenessBreakdown: p.CompletenessBreakdown,
	}

	row, err := r.q.UpdatePersona(ctx, params)
	if err != nil {
		return err
	}

	p.UpdatedAt = row.UpdatedAt.Time
	p.Version = row.Version.Int32
	return nil
}

func (r *PostgresPersonaRepository) GetByUserID(ctx context.Context, userID uuid.UUID) (*domain.Persona, error) {
	row, err := r.q.GetPersonaByUserID(ctx, pgtype.UUID{Bytes: userID, Valid: true})
	if err != nil {
		return nil, err
	}

	return &domain.Persona{
		ID:                 row.ID.Bytes,
		UserID:             row.UserID.Bytes,
		FullNameEncrypted:  row.FullNameEncrypted,
		PreferredName:      row.PreferredName.String,
		Pronouns:           row.Pronouns.String,
		Location:           row.Location,
		WorkAuthorization:  row.WorkAuthorization.String,
		Experience:         row.Experience,
		Education:          row.Education,
		Skills:             row.Skills,
		Certifications:     row.Certifications,
		Preferences:        row.Preferences,
		Personality:        row.Personality,
		BehavioralStories:  row.BehavioralStories,
		CompletenessScore:  row.CompletenessScore.Int32,
		CompletenessBreakdown: row.CompletenessBreakdown,
		Version:            row.Version.Int32,
		CreatedAt:          row.CreatedAt.Time,
		UpdatedAt:          row.UpdatedAt.Time,
	}, nil
}
