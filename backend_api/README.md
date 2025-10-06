# AI Coding Assistant Backend API (FastAPI)

FastAPI backend that proxies prompts to Google Gemini and exposes a simple `/ask` endpoint for the frontend.

## Requirements

- Python 3.10+ (recommended)
- Environment variables:
  - `GOOGLE_API_KEY` (required): Google Generative AI API key for Gemini.
  - Optional:
    - `HOST` (default: `0.0.0.0`)
    - `PORT` (default: `3001`)
    - Any other service configuration your environment requires.

Example `.env`:
```
GOOGLE_API_KEY=your-google-api-key
HOST=0.0.0.0
PORT=3001
```

## Run (Local)

- Install dependencies and run the FastAPI app with Uvicorn (commands may vary depending on your project setup):
  ```
  pip install -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
  ```
- Open API docs: http://localhost:3001/docs
- OpenAPI spec: http://localhost:3001/openapi.json

## Endpoints

- `GET /` — Health check
- `POST /ask` — Accepts JSON: `{ "prompt": "your question" }` and returns aggregated text from Google Gemini.

Request example:
```
POST /ask
Content-Type: application/json

{
  "prompt": "Write a simple Python function to add two numbers."
}
```

Typical response:
```
{
  "output": "def add(a, b):\n    return a + b"
}
```

## CORS

For local development, ensure CORS allows the frontend origin:
- Allowed origin: `http://localhost:3000`
- Methods: at least `POST`, `GET`, `OPTIONS`
- Headers: `Content-Type`, `Accept`

If using FastAPI’s `CORSMiddleware`, configure it similar to:
```python
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Integration Notes

- The React frontend uses `REACT_APP_BACKEND_URL` and defaults to `http://localhost:3001`.
- Ensure this backend is reachable at that URL, and that CORS allows `http://localhost:3000`.
- The frontend calls `POST {REACT_APP_BACKEND_URL}/ask` with `{"prompt": "..."}`
- Verify `GOOGLE_API_KEY` is set before starting the backend.
