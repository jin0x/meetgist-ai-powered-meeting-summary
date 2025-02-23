from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import slack

app = FastAPI(
    title="MeetGist API",
    description="API for MeetGist Slack bot integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Note the prefix change
app.include_router(
    slack.router,
    prefix="/api/v1/events",
    tags=["slack"]
)

# Root health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "MeetGist API is running"}