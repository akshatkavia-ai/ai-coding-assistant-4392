# AI Coding Assistant - Backend API (FastAPI)

FastAPI backend that proxies prompts to Google Gemini and exposes a POST /ask endpoint for the frontend.

- Local default port: http://localhost:3001
- OpenAPI docs: http://localhost:3001/docs
- Preview system note: If using the project preview, ensure this service is running first on port 3001 so the frontend (port 3000) can connect.

## Environment variables

Required:
- GOOGLE_API_KEY

How to provide environment variables:
- Using a .env file (recommended for local development):
  ```
  cd ai-coding-assistant-4392/backend_api
  cp .env.example .env
  # Edit .env and set:
  # GOOGLE_API_KEY=your_google_api_key_here
  ```
- Export from .env into your shell:
  ```
  export $(cat .env | xargs)
  ```
- Or export manually:
  ```
  export GOOGLE_API_KEY=your_real_key_here
  ```

Note: If GOOGLE_API_KEY is missing, the backend will return HTTP 500 for requests that require it (e.g., POST /ask).

### Verify GOOGLE_API_KEY is set
- Show current shell setting:
  ```
  echo "$GOOGLE_API_KEY"
  ```
  If empty, export it from your .env:
  ```
  export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)
  ```
- If the key is not set or is invalid:
  - GET / will still succeed (health check).
  - POST /ask will return 500 with detail: "Server is missing configuration: GOOGLE_API_KEY is not set."
  - Upstream errors from Gemini (e.g., invalid key) will surface as 502 with a descriptive message.

## Quickstart

1) Create environment file and set GOOGLE_API_KEY
```
cd ai-coding-assistant-4392/backend_api
cp .env.example .env
# Edit .env and set:
# GOOGLE_API_KEY=your_google_api_key_here
export $(cat .env | xargs)   # or export manually
```

2) Install dependencies (Python 3.10+)
```
pip install -r requirements.txt
```

3) Run the server on port 3001
```
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

4) Endpoints
- GET / : Health check (returns { "message": "Healthy" })
  - Quick check:
    ```
    curl -s http://localhost:3001/ | jq .
    ```
- POST /ask : Send a prompt to Google Gemini (model: gemini-1.5-flash)
  - Request JSON: { "prompt": "your prompt" }
  - Response JSON: { "output": "AI generated text" }
  - Sample cURL:
    ```
    curl -s -X POST http://localhost:3001/ask \
      -H "Content-Type: application/json" \
      -d '{"prompt":"Say hello from Gemini"}' | jq .
    ```
  - Expected errors:
    - 400 if prompt is empty.
    - 500 if GOOGLE_API_KEY is not set in the environment.
    - 502 if Gemini returns an upstream error (e.g., invalid key) or on network timeouts.

The React frontend calls POST /ask to obtain AI output.

## CORS

For local development and previews, CORS is configured permissively:
```
allow_origins=["*"]
```
This is set in src/api/main.py via CORSMiddleware and allows the frontend at http://localhost:3000 to call the backend by default.

Production: Restrict CORS to your deployed frontend origin, for example:
```
allow_origins=["https://your-frontend.example.com"]
```

## Troubleshooting (quick)

- 500 on /ask (Server configuration error):
  - Ensure GOOGLE_API_KEY is set in the environment.
  - Example: `export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)`
- 502 on /ask (Upstream error/timeouts):
  - Inspect message for details; often due to invalid/expired key or network issues.
- CORS error in browser console:
  - Ensure CORSMiddleware allow_origins includes your frontend origin (http://localhost:3000 for local).
- Frontend cannot reach backend:
  - Confirm backend is running on http://localhost:3001 and frontend on http://localhost:3000.
  - If you change backend port/host, update REACT_APP_BACKEND_URL in the frontend .env.
- Port already in use (3001):
  - Stop the conflicting process or use a different port. If you change the port, set the frontend REACT_APP_BACKEND_URL accordingly.

## Regenerate OpenAPI

Export the OpenAPI schema to interfaces/openapi.json:
```
python -m src.api.generate_openapi
```

This writes the schema to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## End-to-end check (cross-link)

- Backend: Follow this README to set GOOGLE_API_KEY, run uvicorn, verify:
  - `curl http://localhost:3001/` returns `{ "message": "Healthy" }`
  - `curl -X POST http://localhost:3001/ask ...` returns `{ "output": "..." }`
- Frontend: See ai-coding-assistant-4393/frontend_ui/README.md to start the UI and configure REACT_APP_BACKEND_URL if needed.
- In the browser Network tab, confirm POST http://localhost:3001/ask with body `{ "prompt": "..." }` and a 200 response.

## Notes

- No database is used in this project.
- Ensure your Google API key has access to Gemini models.
