package handlers

import (
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/application/service"
	"github.com/maher/stellapply/internal/domain"
	"github.com/maher/stellapply/internal/interfaces/http/dto"
)

type ApplicationHandler struct {
	service *service.ApplicationService
}

func NewApplicationHandler(s *service.ApplicationService) *ApplicationHandler {
	return &ApplicationHandler{service: s}
}

func (h *ApplicationHandler) CreateApplication(c *fiber.Ctx) error {
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}
	userID, _ := uuid.Parse(userIDStr)

	var req dto.CreateApplicationRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	app := &domain.Application{
		UserID:              userID,
		JobID:               req.JobID,
		ResumeID:            req.ResumeID,
		ResumeSnapshot:      req.ResumeSnapshot,
		CoverLetterID:       req.CoverLetterID,
		CoverLetterSnapshot: req.CoverLetterSnapshot,
		Answers:             req.Answers,
		Status:              req.Status,
		SubmissionMode:      req.SubmissionMode,
	}

	if err := h.service.Create(c.Context(), app); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.Status(fiber.StatusCreated).JSON(h.mapToResponse(app))
}

func (h *ApplicationHandler) ListApplications(c *fiber.Ctx) error {
	userIDStr, ok := c.Locals("user_id").(string)
	if !ok {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized"})
	}
	userID, _ := uuid.Parse(userIDStr)

	apps, err := h.service.ListByUserID(c.Context(), userID)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	resp := make([]dto.ApplicationResponse, len(apps))
	for i, a := range apps {
		resp[i] = h.mapToResponse(a)
	}

	return c.JSON(resp)
}

func (h *ApplicationHandler) GetApplication(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}

	app, err := h.service.GetByID(c.Context(), id)
	if err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
	}

	userIDStr, ok := c.Locals("user_id").(string)
	if ok && app.UserID.String() != userIDStr {
		return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
	}

	return c.JSON(h.mapToResponse(app))
}

func (h *ApplicationHandler) UpdateApplication(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}

	existing, err := h.service.GetByID(c.Context(), id)
	if err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
	}

	userIDStr, ok := c.Locals("user_id").(string)
	if ok && existing.UserID.String() != userIDStr {
		return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
	}

	var req dto.UpdateApplicationRequest
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	existing.ResumeID = req.ResumeID
	existing.ResumeSnapshot = req.ResumeSnapshot
	existing.CoverLetterID = req.CoverLetterID
	existing.CoverLetterSnapshot = req.CoverLetterSnapshot
	existing.Answers = req.Answers
	existing.Status = req.Status
	existing.SubmissionMode = req.SubmissionMode
	existing.SubmissionScreenshotUrl = req.SubmissionScreenshotUrl
	existing.ErrorMessage = req.ErrorMessage
	existing.RetryCount = req.RetryCount
	existing.Timeline = req.Timeline

	if err := h.service.Update(c.Context(), existing); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(h.mapToResponse(existing))
}

func (h *ApplicationHandler) DeleteApplication(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid ID"})
	}

	existing, err := h.service.GetByID(c.Context(), id)
	if err != nil {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{"error": "Not found"})
	}

	userIDStr, ok := c.Locals("user_id").(string)
	if ok && existing.UserID.String() != userIDStr {
		return c.Status(fiber.StatusForbidden).JSON(fiber.Map{"error": "Forbidden"})
	}

	if err := h.service.Delete(c.Context(), id); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.SendStatus(fiber.StatusNoContent)
}

func (h *ApplicationHandler) mapToResponse(a *domain.Application) dto.ApplicationResponse {
	return dto.ApplicationResponse{
		ID:                      a.ID,
		UserID:                  a.UserID,
		JobID:                   a.JobID,
		ResumeID:                a.ResumeID,
		ResumeSnapshot:          a.ResumeSnapshot,
		CoverLetterID:           a.CoverLetterID,
		CoverLetterSnapshot:     a.CoverLetterSnapshot,
		Answers:                 a.Answers,
		Status:                  a.Status,
		SubmissionMode:          a.SubmissionMode,
		SubmittedAt:             a.SubmittedAt,
		SubmissionScreenshotUrl: a.SubmissionScreenshotUrl,
		ErrorMessage:            a.ErrorMessage,
		RetryCount:              a.RetryCount,
		Timeline:                a.Timeline,
		CreatedAt:               a.CreatedAt,
		UpdatedAt:               a.UpdatedAt,
	}
}
