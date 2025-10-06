# AI Coding Assistant - Monorepo

This repository contains:
- backend_api: FastAPI backend that proxies prompts to Google Gemini.
- frontend_ui: React frontend (separate workspace) for sending prompts and viewing AI output.

Preview ports (local defaults):
- Frontend UI: http://localhost:3000
- Backend API: http://localhost:3001

Environment variables (summary):
- Backend (required): GOOGLE_API_KEY
- Frontend (optional): REACT_APP_BACKEND_URL (defaults to http://localhost:3001)

CORS:
- Backend is configured permissively for preview (allow_origins=["*"]). Restrict origins for production deployments.

Local preview note:
- Run the backend first on port 3001, then start the frontend on port 3000. The frontend will use REACT_APP_BACKEND_URL or fall back to http://localhost:3001.

## Backend (FastAPI) - Setup and Run

Location: ai-coding-assistant-4392/backend_api

### 1) Create environment file
Copy .env.example and set your Google API key.

```
cd ai-coding-assistant-4392/backend_api
cp .env.example .env
# Edit .env and set:
# GOOGLE_API_KEY=your_google_api_key_here
```

Note: The application requires GOOGLE_API_KEY and will return HTTP 500 if missing. Export the env when running locally, e.g.:

```
export $(cat .env | xargs)
```

### 2) Install dependencies
Use Python 3.10+.

```
pip install -r requirements.txt
```

### 3) Run the server
Run uvicorn on port 3001:

```
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

The API docs are available at:
- http://localhost:3001/docs
- http://localhost:3001/redoc

### 4) Endpoints
- GET /: Health check.
  - Quick check:
    ```
    curl -s http://localhost:3001/ | jq .
    ```
- POST /ask: Send a prompt to Google Gemini (model: gemini-1.5-flash).
  - Request body:
    - { "prompt": "your prompt" }
  - Response:
    - { "output": "AI generated text" }
  - Sample:
    ```
    curl -s -X POST http://localhost:3001/ask \
      -H "Content-Type: application/json" \
      -d '{"prompt":"Say hello from Gemini"}' | jq .
    ```

### 5) Regenerate OpenAPI
The backend includes a utility to export the OpenAPI schema to interfaces/openapi.json.

```
python -m src.api.generate_openapi
```

This writes the schema to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## Frontend (React)

Location: ai-coding-assistant-4393/frontend_ui

- The frontend targets the backend at REACT_APP_BACKEND_URL, defaulting to http://localhost:3001 if not set.
- Ensure the backend CORS setting allows the frontend origin (defaults to permissive for previews).

Setup summary:
```
cd ai-coding-assistant-4393/frontend_ui
cp .env.example .env    # optional; default points to http://localhost:3001
# Optionally edit .env and set:
# REACT_APP_BACKEND_URL=http://localhost:3001
npm install
npm start
# Visit http://localhost:3000
```

## End-to-End Test Steps (Manual)

1) Start Backend:
   ```
   cd ai-coding-assistant-4392/backend_api
   cp .env.example .env
   # Set your actual Google API key in .env
   export $(cat .env | xargs)
   pip install -r requirements.txt
   uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
   ```
   Verify health: curl http://localhost:3001/

2) Start Frontend:
   ```
   cd ai-coding-assistant-4393/frontend_ui
   cp .env.example .env  # optional; default OK for local
   npm install
   npm start
   ```
   Open http://localhost:3000 in your browser.

3) Use the App:
   - Type a prompt and click "Ask AI".
   - Expect AI output rendered in the output card.
   - Network inspector should show POST http://localhost:3001/ask with { "prompt": "..." }.

## Cross-linked end-to-end check

- Backend README: ai-coding-assistant-4392/backend_api/README.md
  - Verify GOOGLE_API_KEY set, GET / health, POST /ask works
- Frontend README: ai-coding-assistant-4393/frontend_ui/README.md
  - Default REACT_APP_BACKEND_URL is http://localhost:3001; override for non-local if needed
  - Troubleshoot using the browser Network tab; map 4xx/5xx to messages as documented

## Troubleshooting (quick)

- Backend 500 (Server configuration error):
  - Ensure GOOGLE_API_KEY is set/exported for the backend.
  - Example (bash): `export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)`
- CORS errors in browser console:
  - Backend is permissive by default; if modified, allow origin http://localhost:3000.
  - Update CORSMiddleware in backend at src/api/main.py.
- Frontend cannot reach backend:
  - Confirm backend is running on http://localhost:3001 and frontend on http://localhost:3000.
  - If using a custom backend URL, set REACT_APP_BACKEND_URL accordingly in ai-coding-assistant-4393/frontend_ui/.env.
- Port already in use:
  - Stop any conflicting service or change the port. If you change backend port, update REACT_APP_BACKEND_URL.

## Notes
- No database is used in this project.
- Ensure your Google API key has access to Gemini models.