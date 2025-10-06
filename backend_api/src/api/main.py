import os
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    prompt: str = Field(..., description="User's natural language prompt to be sent to Google Gemini.")

# PUBLIC_INTERFACE
class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    output: str = Field(..., description="Aggregated text output returned from Google Gemini.")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

app = FastAPI(
    title="AI Coding Assistant Backend API",
    description="FastAPI backend that proxies prompts to Google Gemini.",
    version="0.1.0",
    openapi_tags=[
        {"name": "health", "description": "Health and readiness checks"},
        {"name": "ai", "description": "AI prompt endpoints that interface with Google Gemini"},
    ],
)

# Keep CORS permissive for preview environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For preview; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _get_api_key() -> str:
    """Fetch GOOGLE_API_KEY from environment and raise 500 if missing."""
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is missing configuration: GOOGLE_API_KEY is not set."
        )
    return api_key

@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["ai"],
    summary="Send prompt to Google Gemini",
    description=(
        "Accepts a user's prompt and forwards it to Google Gemini (gemini-1.5-flash) "
        "using the REST API. Returns aggregated text from the first candidate."
    ),
    responses={
        200: {"description": "Successful Gemini response."},
        400: {"description": "Invalid request input."},
        500: {"description": "Server configuration error."},
        502: {"description": "Upstream Gemini error or network issue."},
    },
)
async def ask(body: AskRequest) -> AskResponse:
    """
    Process a user's prompt by calling Google Gemini.

    Parameters:
    - body: AskRequest containing the 'prompt' string.

    Returns:
    - AskResponse with 'output' containing aggregated text content.

    Error handling:
    - 400 if prompt is empty/whitespace.
    - 500 if GOOGLE_API_KEY is missing.
    - 502 for upstream/network/timeouts or invalid response structures from Gemini.
    """
    prompt = (body.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt must not be empty.")

    api_key = _get_api_key()

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    # Configure httpx client with sensible timeouts and error handling
    timeout = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{GEMINI_API_URL}?key={api_key}", json=payload)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Connection to Gemini timed out.")
    except httpx.ReadTimeout:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Read from Gemini timed out.")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Network error contacting Gemini: {exc!s}")

    # Non-2xx responses from Gemini
    if resp.status_code < 200 or resp.status_code >= 300:
        # Try to include upstream error message if present
        detail: str
        try:
            err_json = resp.json()
            detail = err_json.get("error", {}).get("message") or str(err_json)
        except Exception:
            detail = resp.text
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini upstream error ({resp.status_code}): {detail}",
        )

    try:
        data = resp.json()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid JSON received from Gemini.")

    # Parse the Gemini response. Expected structure:
    # { "candidates": [ { "content": { "parts": [ { "text": "..." }, ... ] } } ] }
    try:
        candidates: Optional[List[dict]] = data.get("candidates")
        if not candidates:
            raise KeyError("candidates missing or empty")

        first = candidates[0]
        content = first.get("content") or {}
        parts = content.get("parts") or []

        texts: List[str] = []
        for p in parts:
            t = p.get("text")
            if isinstance(t, str):
                texts.append(t)

        if not texts:
            # Some variants put text in safetyRatings or other fields; handle gracefully
            raise KeyError("No text parts found in Gemini response.")
        aggregated = "\n".join(texts).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected response format from Gemini: {exc!s}",
        )

    return AskResponse(output=aggregated)
