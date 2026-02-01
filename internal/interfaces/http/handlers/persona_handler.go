package handlers

import (
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/application/service"
	"github.com/maher/stellapply/internal/domain"
	"github.com/maher/stellapply/internal/interfaces/http/dto"
)

type PersonaHandler struct {
	service *service.PersonaService
}

func NewPersonaHandler(s *service.PersonaService) *PersonaHandler {
	return &PersonaHandler{service: s}
}

func (h *PersonaHandler) GetPersona(c *fiber.Ctx) error {
	// Retrieve user_id from context (set by AuthMiddleware)
    // NOTE: For dev testing without auth, we might fallback or mock.
    // Assuming middleware populates "user_id" string
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        // Fallback or error. For now, specific fixed UUID for testing if missing?
        // Let's error out to be safe, or use a header if dev mode.
        // For testing "curl" without token, maybe accept header "X-User-ID"
        userIDStr = c.Get("X-User-ID")
        if userIDStr == "" {
		    return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized: No User ID found"})
        }
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid User ID format"})
	}

	persona, err := h.service.GetByUserID(c.Context(), userID)
	if err != nil {
		// Differentiate not found vs error
        if err.Error() == "no rows in result set" {
             return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Persona not found"})
        }
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	// Map to response DTO
    // Manually map fields or use library. Manual for control.
    resp := dto.PersonaResponse{
        ID: persona.ID,
        UserID: persona.UserID,
        PreferredName: persona.PreferredName,
        Pronouns: persona.Pronouns,
        Location: persona.Location,
        WorkAuthorization: persona.WorkAuthorization,
        Experience: persona.Experience,
        Education: persona.Education,
        Skills: persona.Skills,
        Certifications: persona.Certifications,
        Preferences: persona.Preferences,
        Personality: persona.Personality,
        BehavioralStories: persona.BehavioralStories,
        CompletenessScore: persona.CompletenessScore,
        CompletenessBreakdown: persona.CompletenessBreakdown,
        Version: persona.Version,
        CreatedAt: persona.CreatedAt,
        UpdatedAt: persona.UpdatedAt,
    }

	return c.JSON(resp)
}

func (h *PersonaHandler) UpdatePersona(c *fiber.Ctx) error {
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
        if userIDStr == "" {
		    return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized: No User ID found"})
        }
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid User ID format"})
	}

	var req dto.PersonaRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
	}

	// Map DTO to Domain
	persona := &domain.Persona{
		UserID:            userID,
		PreferredName:     req.PreferredName,
		Pronouns:          req.Pronouns,
		Location:          req.Location,
		WorkAuthorization: req.WorkAuthorization,
		Experience:        req.Experience,
		Education:         req.Education,
		Skills:            req.Skills,
		Certifications:    req.Certifications,
		Preferences:       req.Preferences,
		Personality:       req.Personality,
		BehavioralStories: req.BehavioralStories,
        // Calculate/Update completeness in service usually, here we just pass data
	}

	if err := h.service.Update(c.Context(), persona); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(persona)
}
