from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from beanie import Document

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class TagModel(BaseModel):
    """Pydantic model for tag creation/updates"""
    id: Optional[PyObjectId] = Field(default=None)
    name: str
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class Tag(Document):
    """Beanie Document for Tag in database"""
    name: str
    
    class Settings:
        name = "tags"

class TagCollection(BaseModel):
    tags: list[TagModel]
