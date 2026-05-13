import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.org_member import OrgMembership
from app.models.refresh_token import RefreshToken
from app.core.security import (
    hash_password, verify_password,
    build_scopes, create_access_token
)
from app.core.config import settings


# ── Registration ──────────────────────────────────────────────────────────────

async def register_user(db: AsyncSession, email: str, password: str, name: str = None) -> User:
    """
    Create a new user with hashed password.
    Raises ValueError if email already exists.
    """
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        name=name,
        hashed_password=hash_password(password),  # bcrypt hash — never store plain
        is_active=True,
        is_verified=False,   # set True after email verification (future feature)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── Login ─────────────────────────────────────────────────────────────────────

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Verify email + password.
    Raises ValueError if credentials are wrong (generic message — never reveal which).
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("Account is disabled")

    return user


# ── Org memberships ───────────────────────────────────────────────────────────

async def get_memberships_with_orgs(db: AsyncSession, user_id) -> list:
    """
    Load all org memberships for a user, with org details eagerly loaded.
    Used to build JWT scopes.
    """
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.user_id == user_id)
        .options(selectinload(OrgMembership.org))
    )
    return result.scalars().all()


# ── Refresh token ─────────────────────────────────────────────────────────────

async def store_refresh_token(db: AsyncSession, user_id, jti: str) -> None:
    """
    Store the jti of the issued access token as a refresh token in DB.
    Used to validate and rotate tokens at /auth/refresh.
    """
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    db.add(RefreshToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires,
        revoked=False,
    ))
    await db.commit()


async def rotate_refresh_token(db: AsyncSession, jti: str):
    """
    Token refresh flow (from the diagram):
    1. Validate jti exists in DB and is not revoked
    2. Revoke old token (one-time use — rotation pattern)
    3. Re-load memberships from DB (role changes take effect here)
    4. Issue new access token + new refresh token
    Returns (access_token, new_jti, user) or (None, None, None) if invalid.
    """
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.revoked == False,
        )
    )
    stored = result.scalar_one_or_none()

    # Invalid or expired
    if not stored or stored.expires_at < datetime.now(timezone.utc):
        return None, None, None

    # Revoke old token immediately
    stored.revoked = True
    await db.commit()

    # Re-load user
    from sqlalchemy import select as sel
    user_result = await db.execute(select(User).where(User.id == stored.user_id))
    user = user_result.scalar_one()

    # Re-load memberships — if role changed since last login, new token reflects it
    memberships = await get_memberships_with_orgs(db, user.id)
    scopes = build_scopes(memberships)

    # Issue new tokens
    access_token, new_jti = create_access_token(
        str(user.id), user.email, user.name, scopes
    )
    await store_refresh_token(db, user.id, new_jti)

    return access_token, new_jti, user