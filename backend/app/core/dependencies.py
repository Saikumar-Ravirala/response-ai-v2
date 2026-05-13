from fastapi import Request, HTTPException, Depends
from jose import JWTError
from app.core.security import verify_access_token
from app.core.redis_client import is_denylisted

# Higher index = higher permission level
ROLE_HIERARCHY = ["viewer", "member", "admin", "owner"]


async def get_current_user(request: Request) -> dict:
    """
    Injected into every protected route. Does 3 checks:
    1. Reads JWT from httpOnly cookie (browser sends it automatically)
    2. Verifies JWT signature + expiry
    3. Checks Redis denylist (catches tokens revoked on logout)
    Returns the decoded payload dict on success.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

    # Redis denylist check — this is the logout check from the diagram
    if await is_denylisted(payload["jti"]):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    return payload  # {sub, email, name, scopes, jti, exp}


def require_org_role(min_role: str):
    """
    RBAC dependency — pure JWT scope check, zero DB lookups.
    Reads org_slug from the URL path parameter automatically.

    Usage:
        @router.delete('/api/org/{org_slug}/member/{id}')
        async def delete_member(user = Depends(require_org_role('admin'))):
            ...
    """
    async def checker(request: Request, user=Depends(get_current_user)):
        org_slug = request.path_params.get("org_slug")
        if not org_slug:
            raise HTTPException(status_code=400, detail="org_slug missing from path")

        # Find role for this specific org from JWT scopes
        user_role = next(
            (s.split(":")[2] for s in user["scopes"]
             if s.startswith(f"org:{org_slug}:")),
            None
        )

        if not user_role:
            raise HTTPException(status_code=403, detail="Not a member of this org")

        if ROLE_HIERARCHY.index(user_role) < ROLE_HIERARCHY.index(min_role):
            raise HTTPException(
                status_code=403,
                detail=f"Requires {min_role} or above, you have {user_role}"
            )

        return user
    return checker