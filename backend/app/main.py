from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import ALL models here so SQLAlchemy registers them all together
# This fixes the 'Organization' relationship lookup error
from app.models.user import User
from app.models.organization import Organization
from app.models.org_member import OrgMembership
from app.models.refresh_token import RefreshToken
from app.models.call import Call

from app.api.auth import router as auth_router

app = FastAPI(title="Response AI V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}