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
- POST /ask : Send a prompt to Google Gemini (model: gemini-1.5-flash)
  - Request JSON: { "prompt": "your prompt" }
  - Response JSON: { "output": "AI generated text" }

The React frontend calls POST /ask to obtain AI output.

## CORS

For local development and previews, CORS is configured permissively:
```
allow_origins=["*"]
```
This is set in src/api/main.py via CORSMiddleware.

Production: Restrict CORS to your deployed frontend origin, for example:
```
allow_origins=["https://your-frontend.example.com"]
```

## Troubleshooting (quick)

- 500 on /ask (Server configuration error):
  - Ensure GOOGLE_API_KEY is set in the environment.
  - Example: `export $(cat ai-coding-assistant-4392/backend_api/.env | xargs)`
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

## Notes

- No database is used in this project.
- Ensure your Google API key has access to Gemini models.
