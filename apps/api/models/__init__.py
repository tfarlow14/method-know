from .tag import TagModel, Tag, TagCollection
from .resource import (
    ResourceBase,
    ResourceBaseInput,
    ArticleResource,
    ArticleResourceInput,
    CodeSnippetResource,
    CodeSnippetResourceInput,
    LearningResourceBase,
    BookResource,
    BookResourceInput,
    CourseResource,
    CourseResourceInput,
    ResourceModel,
    ResourceModelInput,
    Resource,
    ResourceCollection,
)
from .user import UserModel, User, UserCollection, UserResponse

# Rebuild models to resolve forward references
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

__all__ = [
    "TagModel",
    "Tag",
    "TagCollection",
    "ResourceBase",
    "ArticleResource",
    "CodeSnippetResource",
    "LearningResourceBase",
    "BookResource",
    "CourseResource",
    "ResourceModel",
    "Resource",
    "ResourceCollection",
    "UserModel",
    "User",
    "UserCollection",
    "UserResponse",
]
