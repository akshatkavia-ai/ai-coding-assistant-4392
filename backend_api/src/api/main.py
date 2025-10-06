import os
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class AskRequest(BaseModel):
    """Request model for the /ask endpoint."""
    prompt: str = Field(..., description="User's natural language prompt to be sent to Google Gemini.")

# PUBLIC_INTERFACE
class AskResponse(BaseModel):
    """Response model for the /ask endpoint."""
    output: str = Field(..., description="Aggregated text output returned from Google Gemini.")

# PUBLIC_INTERFACE
class ErrorResponse(BaseModel):
    """Structured error response model."""
    detail: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    hint: str = Field(..., description="Helpful hint for resolving the error")

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

# Global exception handler to ensure all errors return JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exceptions and return structured JSON error."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "code": "INTERNAL_ERROR",
            "hint": "An unexpected error occurred. Please contact support if this persists."
        }
    )

# Override default HTTPException handler to return structured JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return structured JSON for all HTTPExceptions."""
    # Determine appropriate code and hint based on status
    code = "UNKNOWN_ERROR"
    hint = "Please check your request and try again."
    
    if exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "INVALID_REQUEST"
        hint = "Ensure the request body is valid JSON with a 'prompt' field containing a non-empty string."
    elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        code = "VALIDATION_ERROR"
        hint = "Request must include a JSON body with required field: {'prompt': 'your prompt here'}."
    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        code = "SERVER_CONFIG_ERROR"
        hint = "Server configuration issue detected. Verify GOOGLE_API_KEY is set in environment."
    elif exc.status_code == status.HTTP_502_BAD_GATEWAY:
        code = "UPSTREAM_ERROR"
        hint = "Issue communicating with Google Gemini. Verify GOOGLE_API_KEY is valid and has Gemini API access. Check network egress."
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "code": code,
            "hint": hint
        }
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

def _redact_api_key(url: str) -> str:
    """Redact API key from URL for safe logging."""
    if "key=" in url:
        parts = url.split("key=")
        if len(parts) > 1:
            return f"{parts[0]}key=***REDACTED***"
    return url

# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    
    Returns:
        JSON object with status: ok
    
    Example:
        curl -s http://localhost:3001/ | jq .
    """
    return {"status": "ok"}

# PUBLIC_INTERFACE
@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["ai"],
    summary="Send prompt to Google Gemini",
    description=(
        "Accepts a user's prompt and forwards it to Google Gemini (gemini-1.5-flash) "
        "using the REST API. Returns aggregated text from the first candidate.\n\n"
        "**Request payload must be JSON with 'prompt' field:**\n"
        "```json\n"
        '{"prompt": "your prompt here"}\n'
        "```\n\n"
        "**Example curl command:**\n"
        "```bash\n"
        "curl -s -X POST http://localhost:3001/ask \\\n"
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"prompt":"Say hello from Gemini"}\' | jq .\n'
        "```"
    ),
    responses={
        200: {"description": "Successful Gemini response.", "model": AskResponse},
        400: {"description": "Invalid request input.", "model": ErrorResponse},
        422: {"description": "Request validation error - missing or invalid 'prompt' field.", "model": ErrorResponse},
        500: {"description": "Server configuration error.", "model": ErrorResponse},
        502: {"description": "Upstream Gemini error or network issue.", "model": ErrorResponse},
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
    - 422 if request body doesn't match expected schema (missing 'prompt' field).
    - 500 if GOOGLE_API_KEY is missing.
    - 502 for upstream/network/timeouts or invalid response structures from Gemini.
    
    All errors return structured JSON with 'detail', 'code', and 'hint' fields.
    
    Example valid request:
        curl -s -X POST http://localhost:3001/ask \
          -H "Content-Type: application/json" \
          -d '{"prompt":"Explain recursion"}' | jq .
    """
    prompt = (body.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt must not be empty."
        )

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
    
    # Build the full URL for diagnostics (redacted)
    full_url = f"{GEMINI_API_URL}?key={api_key}"
    redacted_url = _redact_api_key(full_url)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Diagnostic: Log the attempt (with redacted key)
            print(f"[DIAG] Attempting POST to Gemini API: {redacted_url}")
            resp = await client.post(full_url, json=payload)
            print(f"[DIAG] Gemini response status: {resp.status_code}")
    except httpx.ConnectTimeout as exc:
        print(f"[DIAG] Connection timeout to Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Connection to Gemini timed out (connect timeout)."
        )
    except httpx.ReadTimeout as exc:
        print(f"[DIAG] Read timeout from Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Read from Gemini timed out (read timeout)."
        )
    except httpx.TimeoutException as exc:
        print(f"[DIAG] General timeout with Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Timeout communicating with Gemini: {str(exc)}"
        )
    except httpx.RequestError as exc:
        print(f"[DIAG] Request error to Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error contacting Gemini: {str(exc)}"
        )
    except Exception as exc:
        print(f"[DIAG] Unexpected error calling Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected error calling Gemini: {str(exc)}"
        )

    # Non-2xx responses from Gemini
    if resp.status_code < 200 or resp.status_code >= 300:
        print(f"[DIAG] Gemini returned non-2xx status: {resp.status_code}")
        # Try to include upstream error message if present
        detail: str
        try:
            err_json = resp.json()
            print(f"[DIAG] Gemini error JSON: {err_json}")
            detail = err_json.get("error", {}).get("message") or str(err_json)
        except Exception as parse_exc:
            print(f"[DIAG] Could not parse Gemini error JSON: {parse_exc}")
            # Safely read response text without consuming stream
            try:
                detail = resp.text[:500]  # Limit to first 500 chars
            except Exception:
                detail = "(unable to read response body)"
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini upstream error (HTTP {resp.status_code}): {detail}"
        )

    # Parse JSON response
    try:
        data = resp.json()
        print(f"[DIAG] Successfully parsed Gemini JSON response")
    except ValueError as exc:
        print(f"[DIAG] Invalid JSON from Gemini: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid JSON received from Gemini."
        )

    # Parse the Gemini response. Expected structure:
    # { "candidates": [ { "content": { "parts": [ { "text": "..." }, ... ] } } ] }
    try:
        candidates: Optional[List[dict]] = data.get("candidates")
        if not candidates:
            print(f"[DIAG] No candidates in Gemini response: {data}")
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
            print(f"[DIAG] No text parts found in Gemini response: {data}")
            raise KeyError("No text parts found in Gemini response.")
        
        aggregated = "\n".join(texts).strip()
        print(f"[DIAG] Successfully extracted {len(texts)} text part(s) from Gemini")
    except Exception as exc:
        print(f"[DIAG] Error parsing Gemini response structure: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected response format from Gemini: {str(exc)}"
        )

    return AskResponse(output=aggregated)
