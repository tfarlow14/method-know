from typing import Optional, Union, Annotated, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field, BeforeValidator
from beanie import Document, Link

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

if TYPE_CHECKING:
    from models.user import UserResponse
    from models.tag import TagModel

# Pydantic models for request/response validation
class ResourceBase(BaseModel):
    """Base Pydantic model for resource validation (response)"""
    id: Optional[PyObjectId] = Field(default=None)
    title: str
    description: str
    user: "UserResponse"  # Required: populated user information for responses
    tags: list["TagModel"] = Field(default_factory=list)  # Optional: 0 to many tags
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

# Input models for creating resources (accept tag_ids instead of tags)
class ResourceBaseInput(BaseModel):
    """Base Pydantic model for resource creation (request)"""
    title: str
    description: str
    tag_ids: list[PyObjectId] = Field(default_factory=list)  # Optional: 0 to many tag IDs
    
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

# Input models for creating resources
class ArticleResourceInput(ResourceBaseInput):
    type: Literal["article"] = "article"
    url: str

class CodeSnippetResourceInput(ResourceBaseInput):
    type: Literal["code_snippet"] = "code_snippet"
    code: str

class BookResourceInput(ResourceBaseInput):
    type: Literal["book"] = "book"

class CourseResourceInput(ResourceBaseInput):
    type: Literal["course"] = "course"

# Discriminated Union for polymorphism (for API validation - response)
ResourceModel = Annotated[
    Union[ArticleResource, CodeSnippetResource, BookResource, CourseResource],
    Field(discriminator="type")
]

# Discriminated Union for input (accepts tag_ids)
ResourceModelInput = Annotated[
    Union[ArticleResourceInput, CodeSnippetResourceInput, BookResourceInput, CourseResourceInput],
    Field(discriminator="type")
]

# Beanie Document classes for database operations
class Resource(Document):
    """Beanie Document for Resource in database"""
    title: str
    description: str
    type: str  # "article", "code_snippet", "book", "course"
    user: Link["User"]  # Required: Link to User document
    tags: list[Link["Tag"]] = Field(default_factory=list)  # Optional: 0 to many Links to Tag documents
    
    # Optional fields for specific resource types
    url: Optional[str] = None  # For article resources
    code: Optional[str] = None  # For code_snippet resources
    
    class Settings:
        name = "resources"
        indexes = ["type"]

class ResourceCollection(BaseModel):
    resources: list[ResourceModel]

# Rebuild models to resolve forward references
def _rebuild_resource_models():
    """Rebuild resource models to resolve forward references"""
    try:
        from models.user import UserResponse, User
        from models.tag import TagModel, Tag
        ResourceBase.model_rebuild()
        ResourceBaseInput.model_rebuild()
        ArticleResource.model_rebuild()
        ArticleResourceInput.model_rebuild()
        CodeSnippetResource.model_rebuild()
        CodeSnippetResourceInput.model_rebuild()
        LearningResourceBase.model_rebuild()
        BookResource.model_rebuild()
        BookResourceInput.model_rebuild()
        CourseResource.model_rebuild()
        CourseResourceInput.model_rebuild()
        ResourceCollection.model_rebuild()
        Resource.model_rebuild()
    except ImportError:
        pass

_rebuild_resource_models()
