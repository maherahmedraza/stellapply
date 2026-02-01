package middleware

import (
	"context"
	"log"

	"github.com/coreos/go-oidc/v3/oidc"
	"github.com/gofiber/fiber/v2"
)

type AuthMiddleware struct {
	Verifier *oidc.IDTokenVerifier
}

func NewAuthMiddleware(issuerURL, clientID string) (*AuthMiddleware, error) {
	// Bypass initialization for dev
	if issuerURL == "bypass" {
		return &AuthMiddleware{Verifier: nil}, nil
	}

	provider, err := oidc.NewProvider(context.Background(), issuerURL)
	if err != nil {
		log.Printf("Warning: Failed to connect to OIDC provider: %v. Using bypass mode.", err)
		return &AuthMiddleware{Verifier: nil}, nil
	}

	verifier := provider.Verifier(&oidc.Config{
		ClientID: clientID,
	})

	return &AuthMiddleware{
		Verifier: verifier,
	}, nil
}

func (m *AuthMiddleware) Protect() fiber.Handler {
	return func(c *fiber.Ctx) error {
		// Hardcoded test user for dev
		c.Locals("user_id", "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
		c.Locals("claims", map[string]interface{}{})

		return c.Next()
	}
}
