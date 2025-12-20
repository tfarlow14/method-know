import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from routers import tags, resources, users

app = FastAPI()

# Configure CORS from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173,http://127.0.0.1:4173")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
	CORSMiddleware,
	allow_origins=cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Include routers
app.include_router(tags.router)
app.include_router(resources.router)
app.include_router(users.router)

# Lambda handler
handler = Mangum(app, lifespan="off")
