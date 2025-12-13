from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_to_mongo, close_mongo_connection
from routers import tags, resources, users

@asynccontextmanager
async def lifespan(app: FastAPI):
	await connect_to_mongo()
	yield
	await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:5173",
		"http://localhost:4173",
		"http://127.0.0.1:5173",
		"http://127.0.0.1:4173",
	],  # Add your frontend URLs
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Include routers
app.include_router(tags.router)
app.include_router(resources.router)
app.include_router(users.router)
