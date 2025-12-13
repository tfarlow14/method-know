from .tag import TagModel, Tag, TagCollection
from .resource import (
    ResourceBase,
    ArticleResource,
    CodeSnippetResource,
    LearningResourceBase,
    BookResource,
    CourseResource,
    ResourceModel,
    Resource,
    ResourceCollection,
)
from .user import UserModel, User, UserCollection, UserResponse

# Rebuild models to resolve forward references after all models are imported
# This must happen after User is imported so Link["User"] can be resolved
ResourceBase.model_rebuild()
ArticleResource.model_rebuild()
CodeSnippetResource.model_rebuild()
LearningResourceBase.model_rebuild()
BookResource.model_rebuild()
CourseResource.model_rebuild()
ResourceCollection.model_rebuild()
# Rebuild the Beanie Document class to resolve Link["User"] forward reference
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
