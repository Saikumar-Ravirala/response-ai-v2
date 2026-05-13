from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.db.session import get_db
from app.services.auth.auth_service import (
    register_user, authenticate_user,
    get_memberships_with_orgs, store_refresh_token, rotate_refresh_token
)
from app.core.security import build_scopes, create_access_token
from app.core.redis_client import add_to_denylist
from app.core.dependencies import get_current_user
from app.models.refresh_token import RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, UserOut
from sqlalchemy import update

router = APIRouter(prefix="/auth", tags=["auth"])

# secure=False for local dev — set True in production (requires HTTPS)
COOKIE_OPTS = dict(httponly=True, secure=False, samesite="lax")


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new account.
    Hashes password with bcrypt before storing.
    Returns the new user's basic info.
    """
    try:
        user = await register_user(db, body.email, body.password, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id":    str(user.id),
        "email": user.email,
        "name":  user.name,
    }


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Login flow (replaces Google OAuth):
    1. Verify email + password
    2. Load org memberships → build JWT scopes
    3. Issue access token (15 min) + refresh token (7 days)
    4. Set both as httpOnly cookies
    5. Return user profile
    """
    try:
        user = await authenticate_user(db, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Load memberships → build scopes (RBAC applied at login)
    memberships = await get_memberships_with_orgs(db, user.id)
    scopes = build_scopes(memberships)

    # Issue JWT access token + store refresh token jti in DB
    access_token, jti = create_access_token(
        str(user.id), user.email, user.name, scopes
    )
    await store_refresh_token(db, user.id, jti)

    # Set httpOnly cookies — browser never sees raw token values
    response.set_cookie("access_token", access_token, max_age=900,          **COOKIE_OPTS)
    response.set_cookie("refresh_jti",  jti,           max_age=60*60*24*7,  **COOKIE_OPTS)

    return {
        "id":     str(user.id),
        "email":  user.email,
        "name":   user.name,
        "scopes": scopes,
    }


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Token refresh flow (from the diagram):
    Called automatically by frontend when it gets a 401.
    Validates refresh jti → rotates → issues new tokens.
    Role changes take effect here because memberships are re-loaded from DB.
    """
    jti = request.cookies.get("refresh_jti")
    if not jti:
        raise HTTPException(status_code=401, detail="No refresh token")

    access_token, new_jti, user = await rotate_refresh_token(db, jti)

    if not access_token:
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    response.set_cookie("access_token", access_token, max_age=900,         **COOKIE_OPTS)
    response.set_cookie("refresh_jti",  new_jti,      max_age=60*60*24*7,  **COOKIE_OPTS)
    return {"ok": True}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Logout flow (from the diagram):
    1. Add access token jti to Redis denylist (instant block, TTL = remaining lifetime)
    2. Revoke all refresh tokens in DB
    3. Clear both cookies
    """
    # Step 1 — Redis denylist (instant block even before JWT expires)
    ttl = max(0, user["exp"] - int(datetime.now(timezone.utc).timestamp()))
    await add_to_denylist(user["jti"], ttl)

    # Step 2 — Revoke refresh tokens in DB
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user["sub"],
            RefreshToken.revoked == False
        )
        .values(revoked=True)
    )
    await db.commit()

    # Step 3 — Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_jti")
    return {"ok": True}


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """
    Returns current user info from JWT — zero DB query needed.
    Scopes show what orgs and roles this user has.
    """
    return {
        "id":     user["sub"],
        "email":  user["email"],
        "name":   user.get("name"),
        "scopes": user["scopes"],
    }