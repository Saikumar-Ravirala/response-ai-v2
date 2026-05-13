from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user, require_scope

router = APIRouter(prefix="/api/org", tags=["members"])

@router.delete("/{org_slug}/member/{member_id}")
async def delete_member(
    org_slug: str,
    member_id: str,
    user=Depends(get_current_user),   # verifies JWT + denylist
):
    """
    RBAC check inline — checks if user has at least 'admin' role for this org.
    Scopes live in the JWT → zero DB lookups for the auth check itself.
    """
    ROLE_HIERARCHY = ["viewer", "member", "admin", "owner"]
    min_role = "admin"

    user_role = next(
        (s.split(":")[2] for s in user["scopes"] if s.startswith(f"org:{org_slug}:")),
        None
    )

    if not user_role or ROLE_HIERARCHY.index(user_role) < ROLE_HIERARCHY.index(min_role):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Need admin or above")

    # ✅ Authorized — do the actual work
    return {"deleted": member_id, "by": user["email"]}