from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import slack

app = FastAPI(
    title="MidGist API",
    description="API for MidGist Slack bot integration",
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

# Include routers
app.include_router(slack.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}