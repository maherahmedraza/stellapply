package handlers

import (
	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"github.com/maher/stellapply/internal/application/service"
)

type PrivacyHandler struct {
	service *service.PrivacyService
}

func NewPrivacyHandler(service *service.PrivacyService) *PrivacyHandler {
	return &PrivacyHandler{service: service}
}

func (h *PrivacyHandler) ExportData(c *fiber.Ctx) error {
	userIDStr := c.Locals("user_id").(string)
	userID, _ := uuid.Parse(userIDStr)

	data, err := h.service.ExportUserData(c.Context(), userID)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	c.Set("Content-Type", "application/json")
	c.Set("Content-Disposition", `attachment; filename="stellapply_data_export.json"`)
	return c.Send(data)
}

func (h *PrivacyHandler) RestrictProcessing(c *fiber.Ctx) error {
	userIDStr := c.Locals("user_id").(string)
	userID, _ := uuid.Parse(userIDStr)

	var req struct {
		Restricted bool `json:"restricted"`
	}
	if err := c.BodyParser(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	if err := h.service.RestrictProcessing(c.Context(), userID, req.Restricted); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(fiber.Map{"message": "Processing restriction updated"})
}

func (h *PrivacyHandler) DeleteAccount(c *fiber.Ctx) error {
	userIDStr := c.Locals("user_id").(string)
	userID, _ := uuid.Parse(userIDStr)

	if err := h.service.DeleteUserAccount(c.Context(), userID); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(fiber.Map{"message": "Account scheduled for deletion with 30-day grace period"})
}
