package persistence

import (
	"context"
	"encoding/json"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/maher/stellapply/internal/domain"
)

type PostgresUserRepository struct {
	q *Queries
}

func NewPostgresUserRepository(q *Queries) *PostgresUserRepository {
	return &PostgresUserRepository{q: q}
}

func (r *PostgresUserRepository) Create(ctx context.Context, u *domain.User) error {
	metadata, _ := json.Marshal(u.GovernanceMetadata)
	params := CreateUserParams{
		EmailEncrypted:     u.EmailEncrypted,
		EmailHash:          u.EmailHash,
		PasswordHash:       u.PasswordHash,
		Status:             pgtype.Text{String: u.Status, Valid: true},
		GovernanceMetadata: metadata,
	}

	row, err := r.q.CreateUser(ctx, params)
	if err != nil {
		return err
	}

	u.ID = row.ID.Bytes
	u.CreatedAt = row.CreatedAt.Time
	u.UpdatedAt = row.UpdatedAt.Time
	return nil
}

func (r *PostgresUserRepository) GetByEmailHash(ctx context.Context, emailHash string) (*domain.User, error) {
	row, err := r.q.GetUserByEmailHash(ctx, emailHash)
	if err != nil {
		return nil, err
	}

	var metadata domain.DataGovernanceMetadata
	_ = json.Unmarshal(row.GovernanceMetadata, &metadata)

	return &domain.User{
		ID:                 row.ID.Bytes,
		ExternalID:         row.ExternalID.Bytes,
		EmailHash:          row.EmailHash,
		EmailEncrypted:     row.EmailEncrypted,
		PasswordHash:       row.PasswordHash,
		Status:             row.Status.String,
		GovernanceMetadata: metadata,
		CreatedAt:          row.CreatedAt.Time,
		UpdatedAt:          row.UpdatedAt.Time,
	}, nil
}

func (r *PostgresUserRepository) GetByID(ctx context.Context, id uuid.UUID) (*domain.User, error) {
	row, err := r.q.GetUserByID(ctx, pgtype.UUID{Bytes: id, Valid: true})
	if err != nil {
		return nil, err
	}

	var metadata domain.DataGovernanceMetadata
	_ = json.Unmarshal(row.GovernanceMetadata, &metadata)

	return &domain.User{
		ID:                 row.ID.Bytes,
		ExternalID:         row.ExternalID.Bytes,
		EmailHash:          row.EmailHash,
		EmailEncrypted:     row.EmailEncrypted,
		PasswordHash:       row.PasswordHash,
		Status:             row.Status.String,
		GovernanceMetadata: metadata,
		CreatedAt:          row.CreatedAt.Time,
		UpdatedAt:          row.UpdatedAt.Time,
	}, nil
}

func (r *PostgresUserRepository) Update(ctx context.Context, u *domain.User) error {
	metadata, _ := json.Marshal(u.GovernanceMetadata)
	params := UpdateUserParams{
		ID:                 pgtype.UUID{Bytes: u.ID, Valid: true},
		EmailHash:          u.EmailHash,
		EmailEncrypted:     u.EmailEncrypted,
		Status:             pgtype.Text{String: u.Status, Valid: true},
		GovernanceMetadata: metadata,
	}
	return r.q.UpdateUser(ctx, params)
}

func (r *PostgresUserRepository) Delete(ctx context.Context, id uuid.UUID) error {
	return r.q.DeleteUser(ctx, pgtype.UUID{Bytes: id, Valid: true})
}
