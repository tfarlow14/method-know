from fastapi import APIRouter, HTTPException, Body, status, Depends
from models.resource import ResourceModel, Resource, ResourceCollection
from models.user import User
from models.tag import Tag
from utils.auth import get_current_user

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", response_model=ResourceModel, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceModel = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Create a new resource (requires authentication)"""
    # Use current user's ID if user_id not provided
    user_id = resource.user_id or str(current_user.id)
    
    # Validate user exists
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    # Validate tags exist
    if resource.tag_ids:
        for tag_id in resource.tag_ids:
            tag = await Tag.get(tag_id)
            if not tag:
                raise HTTPException(status_code=400, detail=f"Tag {tag_id} does not exist")
    
    # Convert Pydantic model to Beanie Document
    resource_dict = resource.model_dump(exclude=["id"])
    new_resource = Resource(
        title=resource_dict["title"],
        description=resource_dict["description"],
        type=resource_dict["type"],
        user_id=user_id,
        tag_ids=resource_dict.get("tag_ids", []),
        url=resource_dict.get("url"),
        code=resource_dict.get("code")
    )
    await new_resource.insert()
    
    # Convert back to Pydantic model for response
    return _resource_doc_to_model(new_resource)

@router.get("", response_model=ResourceCollection)
async def list_resources(
    user_id: str = None,
    _current_user: User = Depends(get_current_user)  # Authentication required
):
    """List resources, optionally filtered by user_id (requires authentication)"""
    # Filter by user_id if provided
    if user_id:
        resources = await Resource.find(Resource.user_id == user_id).to_list()
    else:
        resources = await Resource.find_all().to_list()
    
    # Convert Beanie Documents to Pydantic models
    processed_resources = [_resource_doc_to_model(resource) for resource in resources]
    
    return ResourceCollection(resources=processed_resources)

@router.get("/user/{user_id}", response_model=ResourceCollection)
async def get_resources_by_user(
    user_id: str,
    _current_user: User = Depends(get_current_user)  # Authentication required
):
    """Get all resources for a specific user (requires authentication)"""
    # Validate user exists
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resources = await Resource.find(Resource.user_id == user_id).to_list()
    
    # Convert Beanie Documents to Pydantic models
    processed_resources = [_resource_doc_to_model(resource) for resource in resources]
    
    return ResourceCollection(resources=processed_resources)

def _resource_doc_to_model(resource: Resource) -> ResourceModel:
    """Convert Beanie Resource Document to Pydantic ResourceModel"""
    from models.resource import (
        ArticleResource, CodeSnippetResource, BookResource, CourseResource
    )
    
    base_data = {
        "id": str(resource.id),
        "title": resource.title,
        "description": resource.description,
        "user_id": resource.user_id,
        "tag_ids": resource.tag_ids or []
    }
    
    if resource.type == "article":
        return ArticleResource(**base_data, url=resource.url or "")
    elif resource.type == "code_snippet":
        return CodeSnippetResource(**base_data, code=resource.code or "")
    elif resource.type == "book":
        return BookResource(**base_data)
    elif resource.type == "course":
        return CourseResource(**base_data)
    else:
        raise ValueError(f"Unknown resource type: {resource.type}")
