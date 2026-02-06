# 📝 API Documentation

## Overview
The API is built with **FastAPI** and adheres to **RESTful** principles.
- **Base URL:** `http://localhost:8000/api/v1`
- **Documentation:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc`

## Authentication
All protected endpoints require a Bearer Token (JWT) from Keycloak.
- **Header:** `Authorization: Bearer <token>`

## Key Endpoints

### 🔐 Identity & Auth
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/auth/me` | Get current user profile |
| `POST` | `/auth/refresh` | Refresh access token |

### 📄 Resume
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/resume/upload` | Upload PDF/DOCX for parsing |
| `GET` | `/resume/{id}` | Get structured resume data |
| `PATCH` | `/resume/{id}` | Update resume content |
| `POST` | `/resume/{id}/analyze` | Get AI-driven improvements |

### 💼 Job Search
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/jobs` | Search jobs (supports filters) |
| `POST` | `/jobs/match` | Vector match against persona |
| `GET` | `/jobs/{id}` | Get job details |

### 👤 Persona
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/persona` | Create/Update career persona |
| `GET` | `/persona` | Get active persona |

### 🛡️ GDPR
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/gdpr/consent` | Check consent status |
| `POST` | `/gdpr/export` | Request data export (JSON) |
| `DELETE` | `/gdpr/erasure` | Request account deletion |

## Error Handling
Standard HTTP status codes are used:
- `200`: Success
- `400`: Bad Request (Validation Error)
- `401`: Unauthorized (Invalid/Missing Token)
- `404`: Not Found
- `422`: Validation Error (Pydantic)
- `500`: Internal Server Error
