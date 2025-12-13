from typing import Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field, BeforeValidator
from beanie import Document

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

# Pydantic models for request/response validation
class ResourceBase(BaseModel):
    """Base Pydantic model for resource validation"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    description: str
    user_id: Optional[PyObjectId] = None  # Foreign key to users collection
    tag_ids: list[PyObjectId] = []
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class ArticleResource(ResourceBase):
    type: Literal["article"] = "article"
    url: str

class CodeSnippetResource(ResourceBase):
    type: Literal["code_snippet"] = "code_snippet"
    code: str

# Base class for learning resources (books and courses)
class LearningResourceBase(ResourceBase):
    """Base class for learning resources. Book and Course inherit from this."""
    
    @classmethod
    def is_learning_resource_type(cls, resource_type: str) -> bool:
        """Check if a resource type is a learning resource (book or course)."""
        return resource_type in ("book", "course")

class BookResource(LearningResourceBase):
    type: Literal["book"] = "book"

class CourseResource(LearningResourceBase):
    type: Literal["course"] = "course"

# Discriminated Union for polymorphism (for API validation)
ResourceModel = Annotated[
    Union[ArticleResource, CodeSnippetResource, BookResource, CourseResource],
    Field(discriminator="type")
]

# Beanie Document classes for database operations
class Resource(Document):
    """Beanie Document for Resource in database"""
    title: str
    description: str
    type: str  # "article", "code_snippet", "book", "course"
    user_id: Optional[str] = None
    tag_ids: list[str] = []
    
    # Optional fields for specific resource types
    url: Optional[str] = None  # For article resources
    code: Optional[str] = None  # For code_snippet resources
    
    class Settings:
        name = "resources"
        indexes = ["user_id", "type"]

class ResourceCollection(BaseModel):
    resources: list[ResourceModel]
