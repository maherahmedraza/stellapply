package handlers

import (
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/application/service"
	"github.com/maher/stellapply/internal/domain"
	"github.com/maher/stellapply/internal/interfaces/http/dto"
)

type ResumeHandler struct {
	service *service.ResumeService
}

func NewResumeHandler(s *service.ResumeService) *ResumeHandler {
	return &ResumeHandler{service: s}
}

func (h *ResumeHandler) CreateResume(c *fiber.Ctx) error {
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
        if userIDStr == "" {
		    return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
        }
	}
	userID, _ := uuid.Parse(userIDStr)

	var req dto.CreateResumeRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	resume := &domain.Resume{
		UserID:     userID,
		Name:       req.Name,
		TemplateID: req.TemplateID,
		Content:    req.Content,
		IsPrimary:  req.IsPrimary,
	}

	if err := h.service.Create(c.Context(), resume); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.Status(fiber.StatusCreated).JSON(h.mapToResponse(resume))
}

func (h *ResumeHandler) ListResumes(c *fiber.Ctx) error {
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
        if userIDStr == "" {
		    return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
        }
	}
	userID, _ := uuid.Parse(userIDStr)

	resumes, err := h.service.ListByUserID(c.Context(), userID)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	resp := make([]dto.ResumeResponse, len(resumes))
	for i, r := range resumes {
		resp[i] = h.mapToResponse(r)
	}

	return c.JSON(resp)
}

func (h *ResumeHandler) GetResume(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}

	resume, err := h.service.GetByID(c.Context(), id)
	if err != nil {
        // TODO: distinct not found vs error
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
	}

    // Security check: ensure user owns this resume
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
	}
    if userIDStr != "" && resume.UserID.String() != userIDStr {
        return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
    }

	return c.JSON(h.mapToResponse(resume))
}

func (h *ResumeHandler) UpdateResume(c *fiber.Ctx) error {
    idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}
    
    // Check existence and ownership first
    // Simplify: just try to update, if repo checks ID? 
    // Repo update by ID.
    // Ideally service handles this.
    // For now, load it to check ownership.
    existing, err := h.service.GetByID(c.Context(), id)
    if err != nil {
        return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
    }
    
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
	}
    if userIDStr != "" && existing.UserID.String() != userIDStr {
        return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
    }

	var req dto.UpdateResumeRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}
    
    existing.Name = req.Name
    existing.TemplateID = req.TemplateID
    existing.Content = req.Content
    existing.IsPrimary = req.IsPrimary

	if err := h.service.Update(c.Context(), existing); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(h.mapToResponse(existing))
}

func (h *ResumeHandler) mapToResponse(r *domain.Resume) dto.ResumeResponse {
	return dto.ResumeResponse{
		ID:              r.ID,
		UserID:          r.UserID,
		Name:            r.Name,
		TemplateID:      r.TemplateID,
		Content:         r.Content,
		PdfUrl:          r.PdfUrl,
		DocxUrl:         r.DocxUrl,
		AtsScore:        r.AtsScore,
		AnalysisResults: r.AnalysisResults,
		AnalyzedAt:      r.AnalyzedAt,
		IsPrimary:       r.IsPrimary,
		Version:         r.Version,
		CreatedAt:       r.CreatedAt,
		UpdatedAt:       r.UpdatedAt,
	}
}

func (h *ResumeHandler) DeleteResume(c *fiber.Ctx) error {
    idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}
    
    // Check ownership
    existing, err := h.service.GetByID(c.Context(), id)
    if err != nil {
         log.Printf("Delete error: %v", err)
         // If already gone, that's fine? Or 404.
         return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
    }
    
    userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
        userIDStr = c.Get("X-User-ID")
	}
    if userIDStr != "" && existing.UserID.String() != userIDStr {
        return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
    }

    if err := h.service.Delete(c.Context(), id); err != nil {
        return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
    }
    
    return c.SendStatus(fiber.StatusNoContent)
}
