package main

import (
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/maher/stellapply/internal/application/service"
	"github.com/maher/stellapply/internal/infrastructure/external"
	"github.com/maher/stellapply/internal/infrastructure/persistence"
	"github.com/maher/stellapply/internal/interfaces/http/handlers"
	"github.com/maher/stellapply/internal/interfaces/http/middleware"
	"github.com/maher/stellapply/pkg/config"
)

func main() {
	// 1. Load Configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// 2. Database Connection
	dbPool, err := persistence.NewDB(cfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer dbPool.Close()

	// 3. Infrastructure (Repositories)
	queries := persistence.New(dbPool)
	userRepo := persistence.NewPostgresUserRepository(queries)
	personaRepo := persistence.NewPostgresPersonaRepository(queries)
	resumeRepo := persistence.NewPostgresResumeRepository(queries)
	appRepo := persistence.NewPostgresApplicationRepository(queries)

	// 4. Infrastructure (External)
	aiClient := external.NewAIClient(cfg.App.AiServiceUrl)

	// 5. Application (Services)
	personaService := service.NewPersonaService(personaRepo, userRepo)
	resumeService := service.NewResumeService(resumeRepo, aiClient)
	appService := service.NewApplicationService(appRepo)
	privacyService := service.NewPrivacyService(userRepo, personaRepo, resumeRepo, appRepo)

	// 6. Interface (Handlers)
	personaHandler := handlers.NewPersonaHandler(personaService)
	resumeHandler := handlers.NewResumeHandler(resumeService)
	resumeAnalysisHandler := handlers.NewResumeAnalysisHandler(resumeService)
	appHandler := handlers.NewApplicationHandler(appService)
	privacyHandler := handlers.NewPrivacyHandler(privacyService)

	// 6. Setup Fiber
	app := fiber.New(fiber.Config{
		AppName: "Stellapply API",
	})

	// Middleware
	app.Use(logger.New())
	app.Use(cors.New())

	// Auth Middleware Setup (Non-blocking: if Keycloak is down, app still starts but auth fails)
	// In production, you might want to block or retry.
	// Issuer URL: http://localhost:8081/realms/stellapply (external) or http://keycloak:8080/realms/stellapply (internal)
	// We use internal for backend communication if possible, but OIDC provider verification often requires public URL access if validating externally.
	// Docker networking: http://keycloak:8080/realms/stellapply

	authMiddleware, err := middleware.NewAuthMiddleware("bypass", "stellapply-api")
	if err != nil {
		log.Printf("Warning: Auth middleware initialization failed: %v", err)
	}

	// NOTE: Authenticated routes disabled for initial dev loop until Keycloak is fully configured with realm.
	// Uncommenting above requires Keycloak to be healthy and realm 'stellapply' to exist.

	// 7. Routes
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"status":  "ok",
			"message": "Stellapply API is running",
		})
	})

	// API Group
	api := app.Group("/api")
	v1 := api.Group("/v1")

	if authMiddleware != nil {
		v1.Use(authMiddleware.Protect())
	}

	// Persona Routes
	v1.Get("/persona", personaHandler.GetPersona)
	v1.Put("/persona", personaHandler.UpdatePersona)

	// Resume Routes
	v1.Post("/resumes", resumeHandler.CreateResume)
	v1.Get("/resumes", resumeHandler.ListResumes)
	v1.Get("/resumes/:id", resumeHandler.GetResume)
	v1.Put("/resumes/:id", resumeHandler.UpdateResume)
	v1.Delete("/resumes/:id", resumeHandler.DeleteResume)

	// Resume Analysis
	v1.Post("/resumes/:id/analyze", resumeAnalysisHandler.AnalyzeResume)

	// Application Routes
	v1.Post("/applications", appHandler.CreateApplication)
	v1.Get("/applications", appHandler.ListApplications)
	v1.Get("/applications/:id", appHandler.GetApplication)
	v1.Put("/applications/:id", appHandler.UpdateApplication)
	v1.Delete("/applications/:id", appHandler.DeleteApplication)

	// Privacy & GDPR Routes
	v1.Get("/privacy/export", privacyHandler.ExportData)
	v1.Put("/privacy/restrict", privacyHandler.RestrictProcessing)
	v1.Delete("/privacy/delete", privacyHandler.DeleteAccount)

	// 8. Start Server
	log.Printf("Starting server on port %s", cfg.App.Port)
	if err := app.Listen(":" + cfg.App.Port); err != nil {
		log.Fatalf("Server connection error: %v", err)
	}
}
