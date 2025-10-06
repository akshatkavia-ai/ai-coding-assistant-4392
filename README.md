# AI Coding Assistant - Monorepo

This repository contains:
- backend_api: FastAPI backend that proxies prompts to Google Gemini.
- frontend_ui: React frontend for sending prompts and viewing AI output.

Local ports:
- Frontend UI: http://localhost:3000
- Backend API: http://localhost:3001

Environment variables:
- Backend (required): GOOGLE_API_KEY
- Frontend (optional): REACT_APP_BACKEND_URL (defaults to http://localhost:3001)

CORS:
- Backend is permissive for preview (allow_origins=["*"]). Restrict origins for production.

Local preview note:
- Run backend first on port 3001, then frontend on port 3000. Frontend uses REACT_APP_BACKEND_URL or falls back to http://localhost:3001.

## Quickstart (end-to-end)

1) Backend (FastAPI)
```
cd ai-coding-assistant-4392/backend_api
cp .env.example .env
# Edit .env and set:
# GOOGLE_API_KEY=your_google_api_key_here
export $(cat .env | xargs)
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```
Verify:
```
curl -s http://localhost:3001/ | jq .
curl -s -X POST http://localhost:3001/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello from Gemini"}' | jq .
```

2) Frontend (React)
```
cd ai-coding-assistant-4393/frontend_ui
cp .env.example .env    # optional, default points to http://localhost:3001
# REACT_APP_BACKEND_URL=http://localhost:3001  # set if using a non-default backend
npm install
npm start
# Visit http://localhost:3000
```

Cross-links:
- Backend README: ai-coding-assistant-4392/backend_api/README.md
- Frontend README: ai-coding-assistant-4393/frontend_ui/README.md

## Backend (details)

OpenAPI docs:
- http://localhost:3001/docs
- http://localhost:3001/redoc

Endpoints:
- GET / : health
  ```
  curl -s http://localhost:3001/ | jq .
  ```
- POST /ask : body { "prompt": "..." }, returns { "output": "..." }
  ```
  curl -s -X POST http://localhost:3001/ask \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Say hello from Gemini"}' | jq .
  ```

Regenerate OpenAPI:
```
python -m src.api.generate_openapi
```
Writes to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## Frontend (details)

- Uses REACT_APP_BACKEND_URL to reach backend (default http://localhost:3001).
- Ensure backend CORS allows http://localhost:3000 (default permissive).

Setup summary:
```
cd ai-coding-assistant-4393/frontend_ui
cp .env.example .env
npm install
npm start
```

## Troubleshooting

- Backend 500 on /ask:
  - GOOGLE_API_KEY missing. Export from .env: `export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)`
- 502 on /ask:
  - Upstream Gemini error or timeout. Check error details.
- CORS errors:
  - Ensure backend allows http://localhost:3000 in src/api/main.py.
- Frontend cannot reach backend:
  - Confirm backend at http://localhost:3001 and frontend at http://localhost:3000.
  - If backend URL differs, set REACT_APP_BACKEND_URL in ai-coding-assistant-4393/frontend_ui/.env and restart.
- Port conflicts:
  - Free the port(s) or change ports; if backend port changes, update REACT_APP_BACKEND_URL.

## Notes

- No database is used.
- Ensure your Google API key has access to Gemini models.