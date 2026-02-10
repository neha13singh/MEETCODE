from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
print(f"DEBUG: Loading settings. CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex='.*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.api import auth, users

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

from app.api import questions, submissions
app.include_router(questions.router, prefix=f"{settings.API_V1_STR}/questions", tags=["questions"])
app.include_router(submissions.router, prefix=f"{settings.API_V1_STR}/submissions", tags=["submissions"])

from app.api import websocket, matches
app.include_router(websocket.router, tags=["websocket"])
app.include_router(matches.router, prefix=f"{settings.API_V1_STR}/matches", tags=["matches"])

@app.get("/")
async def root():
    return {"message": "Welcome to MeetCode API"}
