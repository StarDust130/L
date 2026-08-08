from app.core.config import get_settings
from clerk_backend_api import (
    AuthenticateRequestOptions,
    authenticate_request,
)
from fastapi import HTTPException, Request

"""
Read Authorization header
        ↓
Find Clerk token
        ↓
Ask Clerk SDK to verify it
        ↓
Read the token's user ID
        ↓
Allow or reject the request
"""


def require_user(request: Request) -> str:
    settings = get_settings()

    request_state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.clerk_secret_key,
            authorized_parties=settings.clerk_authorized_parties,
            accepts_token=["session_token"],
        ),
    )

    if not request_state.is_signed_in or not request_state.payload:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    user_id = request_state.payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing",
        )

    return str(user_id)
