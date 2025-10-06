# AI Coding Assistant - Monorepo

This repository contains:
- backend_api: FastAPI backend that proxies prompts to Google Gemini.
- frontend_ui: React frontend (in a separate workspace) for sending prompts and viewing AI output.

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

Note: The application reads GOOGLE_API_KEY from the environment. Ensure it is exported when running locally, e.g.:

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
- POST /ask: Send a prompt to Google Gemini (model: gemini-1.5-flash).
  - Request body:
    - { "prompt": "your prompt" }
  - Response:
    - { "output": "AI generated text" }

CORS is permissive for preview; restrict origins in production.

### 5) Regenerate OpenAPI
The backend includes a utility to export the OpenAPI schema to interfaces/openapi.json.

```
python -m src.api.generate_openapi
```

This writes the schema to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## Frontend (React)
The frontend is located in a separate workspace (ai-coding-assistant-4393/frontend_ui). It targets the backend at http://localhost:3001 by default (ensure CORS is enabled as configured).

## Notes
- No database is used in this project.
- Ensure your Google API key has access to Gemini models.