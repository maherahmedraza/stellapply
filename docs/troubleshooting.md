# 🔧 Troubleshooting

## Common Issues

### 1. Database Connection Failed
**Error:** `Connection refused` or `Cannot connect to server`
- **Fix:** Ensure Docker container is running:
  ```bash
  docker ps | grep postgres
  ```
- **Fix:** Check if port 5432 is occupied by a local Postgres system service.

### 2. "Gemini API Key Missing"
**Error:** Backend creates resumes but they are empty or fail.
- **Fix:** Verify `GEMINI_API_KEY` is set in `.env` and is valid. You can test it using `curl` against Google's API documentation.

### 3. Frontend "Network Error"
**Error:** Cannot login or fetch data.
- **Fix:** Check CORS settings. If Frontend is on port 3000, ensure `ALLOWED_ORIGINS=["http://localhost:3000"]` in Backend `.env`.
- **Fix:** Ensure Backend is running on port 8000.

### 4. Keycloak Redirect Loop or Login Failure
**Error:** "Invalid parameter: redirect_uri"
- **Fix:** In Keycloak Admin Console -> Clients -> `stellapply-frontend`:
    - Ensure **Valid Redirect URIs** includes `http://localhost:3000/*` directly.
    - Ensure **Web Origins** includes `+` or `http://localhost:3000`.

## Logs
- **Backend:** `docker compose logs -f backend` or check `backend.log`.
- **Frontend:** Check browser console (F12) and terminal output.
