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
    
    from models import User, Tag, Resource
    
    # Initialize Beanie with the database and document models
    await init_beanie(
        database=database,
        document_models=[User, Tag, Resource]
    )

async def close_mongo_connection():
    if Database.client:
        Database.client.close()
