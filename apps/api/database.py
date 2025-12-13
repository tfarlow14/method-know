from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

MONGO_URL = "mongodb://localhost:27017/knowledgehub"

class Database:
    client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    """Initialize MongoDB connection and Beanie"""
    Database.client = AsyncIOMotorClient(MONGO_URL)
    database = Database.client.get_database("knowledgehub")
    
    # Import models from __init__.py to ensure all model rebuilds have happened
    # This ensures forward references like Link["User"] are resolved
    from models import User, Tag, Resource
    
    # Ensure Resource model is rebuilt after User is imported
    # This resolves the Link["User"] forward reference
    Resource.model_rebuild()
    
    # Initialize Beanie with the database and document models
    await init_beanie(
        database=database,
        document_models=[User, Tag, Resource]
    )

async def close_mongo_connection():
    if Database.client:
        Database.client.close()
