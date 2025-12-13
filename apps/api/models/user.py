from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict, EmailStr
from beanie import Document

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    """Pydantic model for user creation/updates"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # Note: In production, this should be hashed

class User(Document):
    """Beanie Document for User in database"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # Hashed password
    
    class Settings:
        name = "users"
        indexes = ["email"]  # Index for faster email lookups

class UserResponse(BaseModel):
    """User model without password for responses"""
    id: Optional[PyObjectId] = Field(default=None)
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class UserCollection(BaseModel):
    users: list[UserResponse]
