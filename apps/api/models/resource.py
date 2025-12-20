from typing import Optional, Union, Literal, TYPE_CHECKING, Annotated
from datetime import datetime
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from models.user import UserResponse
    from models.tag import TagModel

class ResourceBase(BaseModel):
    id: Optional[str] = Field(default=None)
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
    tag_ids: list[str] = Field(default_factory=list)
    
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

class Resource(BaseModel):
    """Resource model for DynamoDB"""
    resource_id: str
    title: str
    description: str
    type: str
    user_id: str
    tag_ids: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    code: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "Resource":
        """Create Resource from DynamoDB item."""
        created_at = None
        if 'created_at' in item:
            try:
                created_at = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return cls(
            resource_id=item.get('resource_id', ''),
            title=item.get('title', ''),
            description=item.get('description', ''),
            type=item.get('type', ''),
            user_id=item.get('user_id', ''),
            tag_ids=item.get('tag_ids', []),
            url=item.get('url'),
            code=item.get('code'),
            author=item.get('author'),
            created_at=created_at
        )
    
    def to_dynamodb_item(self) -> dict:
        """Convert Resource to DynamoDB item."""
        item = {
            'resource_id': self.resource_id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'user_id': self.user_id,
            'tag_ids': self.tag_ids,
        }
        if self.url is not None:
            item['url'] = self.url
        if self.code is not None:
            item['code'] = self.code
        if self.author is not None:
            item['author'] = self.author
        if self.created_at:
            item['created_at'] = self.created_at.isoformat()
        return item
    
    @property
    def id(self) -> str:
        """Alias for resource_id for compatibility."""
        return self.resource_id

class ResourceCollection(BaseModel):
    resources: list[ResourceModel]

