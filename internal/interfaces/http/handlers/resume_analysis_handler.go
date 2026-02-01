package handlers

import (
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/application/service"
)

type ResumeAnalysisHandler struct {
	service *service.ResumeService
}

func NewResumeAnalysisHandler(service *service.ResumeService) *ResumeAnalysisHandler {
	return &ResumeAnalysisHandler{service: service}
}

func (h *ResumeAnalysisHandler) AnalyzeResume(c *fiber.Ctx) error {
    idParam := c.Params("id")
    id, err := uuid.Parse(idParam)
    if err != nil {
        return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "invalid resume id"})
    }

    // Basic ownership check logic should ideally be here or in middleware
    // For MVP/Proto, assume authorized if he can call this endpoint with valid ID
    // or rely on a wrapper that checks retrieval first.
    // NOTE: The service's GetByID checks existence, but not ownership logic (that's usually checking UserID against X-User-ID).
    
    // Check ownership before analysis to save AI tokens
    userID, err := uuid.Parse(c.Get("X-User-ID"))
    if err == nil {
        // Fetch to check user_id
        current, err := h.service.GetByID(c.Context(), id)
        if err != nil {
            return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "resume not found"}) 
        }
        if current.UserID != userID {
             return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "forbidden"})
        }
    }

    updatedResume, err := h.service.Analyze(c.Context(), id)
    if err != nil {
        return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
    }

    return c.JSON(updatedResume)
}
