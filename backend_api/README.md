# AI Coding Assistant - Backend API (FastAPI)

FastAPI backend that proxies prompts to Google Gemini and exposes a POST /ask endpoint for the frontend.

- Local default port: http://localhost:3001
- OpenAPI docs: http://localhost:3001/docs

## Environment variables

See .env.example for required variables.

Required:
- GOOGLE_API_KEY

How to provide environment variables:
- Using dotenv-style export:
  ```
  export $(cat .env | xargs)
  ```
- Or export manually in your shell:
  ```
  export GOOGLE_API_KEY=your_real_key_here
  ```

Note: If GOOGLE_API_KEY is missing, the backend will return HTTP 500 for requests that require it (e.g., POST /ask).

Local preview note:
- Run this service first (port 3001), then start the React frontend (port 3000). The frontend will point to http://localhost:3001 unless REACT_APP_BACKEND_URL is set.

## Quickstart

1) Create environment file
```
cd ai-coding-assistant-4392/backend_api
cp .env.example .env
# Edit .env and set:
# GOOGLE_API_KEY=your_google_api_key_here
```

2) Install dependencies (Python 3.10+)
```
pip install -r requirements.txt
```

3) Run the server on port 3001
```
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

4) Use the API
- Health check: GET /
- Prompt endpoint: POST /ask
  - Request: { "prompt": "your prompt" }
  - Response: { "output": "AI generated text" }

The frontend will call POST /ask to obtain AI output.

## CORS

For local development and previews, CORS is configured permissively with:
```
allow_origins=["*"]
```

For production, restrict CORS to your deployed frontend origin, for example:
```
allow_origins=["https://your-frontend.example.com"]
```
Adjust this in src/api/main.py where the CORSMiddleware is added.

## Troubleshooting (quick)

- 500 on /ask due to configuration:
  - Verify GOOGLE_API_KEY is set in environment. Example: `export $(cat .env | xargs)`
- CORS error in browser:
  - Ensure CORSMiddleware allow_origins includes your frontend origin (http://localhost:3000 for local).
- Port in use:
  - Stop the conflicting process or change port. If you change backend port, update REACT_APP_BACKEND_URL in the frontend .env.

## Regenerate OpenAPI

Export the OpenAPI schema to interfaces/openapi.json:
```
python -m src.api.generate_openAPI
```

This writes the schema to ai-coding-assistant-4392/backend_api/interfaces/openapi.json.

## Notes

- No database is used in this project.
- Ensure your Google API key has access to Gemini models.
