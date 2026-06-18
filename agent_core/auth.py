import os
import hashlib
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def verify_api_key(request: Request, call_next):
    """Middleware to verify API key on protected endpoints.

    Set API_KEY in .env to enable authentication.
    Leave it empty to skip auth (default for development).
    """
    api_key = os.getenv("API_KEY", "")
    if not api_key:
        return call_next(request)

    auth_header = request.headers.get("Authorization", "")
    provided_key = auth_header.replace("Bearer ", "")

    if not provided_key or provided_key != api_key:
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid or missing API key"},
        )

    return call_next(request)


def require_auth(request: Request):
    """Decorator to require API key on specific routes."""
    api_key = os.getenv("API_KEY", "")
    if not api_key:
        return

    auth_header = request.headers.get("Authorization", "")
    provided_key = auth_header.replace("Bearer ", "")

    if not provided_key or provided_key != api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
