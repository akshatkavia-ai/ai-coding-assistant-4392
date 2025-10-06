# AI Coding Assistant - Backend API (FastAPI)

FastAPI backend that proxies prompts to Google Gemini and exposes:
- GET /            -> health check
- POST /ask        -> prompt to Gemini, returns { "output": "<text>" }

Ports and docs:
- Backend API (local): http://localhost:3001
- OpenAPI docs:       http://localhost:3001/docs
- Redoc:              http://localhost:3001/redoc

Preview note: Start this backend first on port 3001, then the frontend on port 3000.

## Quickstart

1) Set environment variable GOOGLE_API_KEY
```
cd ai-coding-assistant-4392/backend_api
cp .env.example .env
# Edit .env and set:
# GOOGLE_API_KEY=your_google_api_key_here
export $(cat .env | xargs)   # or: export GOOGLE_API_KEY=your_real_key_here
```

2) Install dependencies (Python 3.10+)
```
pip install -r requirements.txt
```

3) Run on port 3001
```
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

4) Verify endpoints with curl
- GET /
```
curl -s http://localhost:3001/ | jq .
```
- POST /ask
```
curl -s -X POST http://localhost:3001/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello from Gemini"}' | jq .
```

## Environment variables

Required:
- GOOGLE_API_KEY

Ways to set:
- .env file (recommended locally)
  ```
  cd ai-coding-assistant-4392/backend_api
  cp .env.example .env
  # GOOGLE_API_KEY=your_google_api_key_here
  export $(cat .env | xargs)
  ```
- Manual export
  ```
  export GOOGLE_API_KEY=your_real_key_here
  ```

Check the value:
```
echo "$GOOGLE_API_KEY"
```

Behavior:
- If GOOGLE_API_KEY is missing: GET / works; POST /ask returns 500 with configuration error.
- If invalid/expired: POST /ask returns 502 with upstream error details from Gemini.

## End-to-end checklist

- Backend running at http://localhost:3001
- GOOGLE_API_KEY exported in the backend shell
- Frontend running at http://localhost:3000
- From a terminal:
  - GET / returns { "message": "Healthy" }
  - POST /ask returns { "output": "..." }
- In the browser Network tab (on the frontend):
  - POST http://localhost:3001/ask returns 200 with { "output": "..." }

Cross-link: See frontend UI README at ai-coding-assistant-4393/frontend_ui/README.md for REACT_APP_BACKEND_URL setup and UI steps.

## CORS

Local/preview: permissive
```
allow_origins=["*"]
```
Configured in src/api/main.py via CORSMiddleware, enabling calls from http://localhost:3000.

Production: restrict to your frontend origin, for example:
```
allow_origins=["https://your-frontend.example.com"]
```

## Troubleshooting

- 400 on /ask:
  - Prompt likely empty. Ensure JSON includes a non-empty "prompt".
- 500 on /ask (Server configuration):
  - GOOGLE_API_KEY not set. Export from .env:
    `export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)`
- 502 on /ask (Upstream/timeouts):
  - Often invalid/expired key or network issues. Check detail message.
- CORS blocked in browser:
  - Ensure allow_origins includes http://localhost:3000 in src/api/main.py.
- Frontend cannot reach backend:
  - Confirm backend at http://localhost:3001 and frontend at http://localhost:3000.
  - If backend URL/port changed, update REACT_APP_BACKEND_URL in the frontend .env.
- Port 3001 already in use:
  - Stop conflicting process or change port and update the frontend REACT_APP_BACKEND_URL.

## Regenerate OpenAPI

Export OpenAPI to interfaces/openapi.json:
```
python -m src.api.generate_openapi
```
The file is written to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## Notes

- No database is used.
- Your GOOGLE_API_KEY must have access to Gemini models.
