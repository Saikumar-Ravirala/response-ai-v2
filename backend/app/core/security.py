import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain password with bcrypt before storing in DB."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check plain password against stored bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── Refresh token hashing ─────────────────────────────────────────────────────

def hash_token(raw: str) -> str:
    """SHA-256 hash for refresh tokens stored in DB."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ── JWT scopes ────────────────────────────────────────────────────────────────

def build_scopes(memberships: list) -> list[str]:
    """
    Convert DB memberships into JWT scope strings.
    e.g. org_slug='acme', role='admin' → 'org:acme:admin'
    Empty list if user has no org memberships yet.
    """
    scopes = []
    for m in memberships:
        if m.org:
            scopes.append(f"org:{m.org.slug}:{m.role.value}")
    return scopes


# ── JWT creation & verification ───────────────────────────────────────────────

def create_access_token(
    user_id: str,
    email: str,
    name: str,
    scopes: list[str]
) -> tuple[str, str]:
    """
    Create a signed JWT access token.
    Returns (token_string, jti).
    jti is stored with the refresh token so we can revoke this specific token.
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub":    user_id,   # user's DB UUID
        "email":  email,
        "name":   name,
        "scopes": scopes,    # ["org:acme:admin", "org:globex:member"]
        "jti":    jti,       # unique token ID — used for Redis denylist
        "exp":    expire,
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return token, jti


def verify_access_token(token: str) -> dict:
    """
    Verify JWT signature and expiry.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )