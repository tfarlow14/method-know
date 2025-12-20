from typing import Optional, Union, Annotated, Literal, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator
from beanie import Document, Link

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

if TYPE_CHECKING:
    from models.user import UserResponse
    from models.tag import TagModel

class ResourceBase(BaseModel):
    id: Optional[PyObjectId] = Field(default=None)
    title: str
    description: str
    user: "UserResponse"
    tags: list["TagModel"] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class ResourceBaseInput(BaseModel):
    title: str
    description: str
    tag_ids: list[PyObjectId] = Field(default_factory=list)
    
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

class LearningResourceBase(ResourceBase):
    author: Optional[str] = None

class BookResource(LearningResourceBase):
    type: Literal["book"] = "book"
    author: Optional[str] = None

class CourseResource(LearningResourceBase):
    type: Literal["course"] = "course"
    author: Optional[str] = None

class ArticleResourceInput(ResourceBaseInput):
    type: Literal["article"] = "article"
    url: str

class CodeSnippetResourceInput(ResourceBaseInput):
    type: Literal["code_snippet"] = "code_snippet"
    code: str

class BookResourceInput(ResourceBaseInput):
    type: Literal["book"] = "book"
    author: Optional[str] = None

class CourseResourceInput(ResourceBaseInput):
    type: Literal["course"] = "course"
    author: Optional[str] = None

ResourceModel = Annotated[
    Union[ArticleResource, CodeSnippetResource, BookResource, CourseResource],
    Field(discriminator="type")
]

ResourceModelInput = Annotated[
    Union[ArticleResourceInput, CodeSnippetResourceInput, BookResourceInput, CourseResourceInput],
    Field(discriminator="type")
]

class Resource(Document):
    title: str
    description: str
    type: str
    user: Link["User"]
    tags: list[Link["Tag"]] = Field(default_factory=list)
    url: Optional[str] = None
    code: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "resources"
        indexes = ["type"]

class ResourceCollection(BaseModel):
    resources: list[ResourceModel]

