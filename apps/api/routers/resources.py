from fastapi import APIRouter, HTTPException, Body, status, Depends
from models.resource import ResourceModel, ResourceModelInput, Resource, ResourceCollection
from models.user import User
from models.tag import Tag
from utils.auth import get_current_user
import asyncio

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", response_model=ResourceModel, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceModelInput = Body(...),
    current_user: User = Depends(get_current_user)
):
    resource_dict = resource.model_dump(exclude=["tag_ids"])
    
    tag_links = []
    if resource.tag_ids:
        tags = await asyncio.gather(*[Tag.get(tag_id) for tag_id in resource.tag_ids])
        for i, tag in enumerate(tags):
            if not tag:
                raise HTTPException(status_code=400, detail=f"Tag {resource.tag_ids[i]} does not exist")
        tag_links = tags
    
    new_resource = Resource(
        title=resource_dict["title"],
        description=resource_dict["description"],
        type=resource_dict["type"],
        user=current_user,
        tags=tag_links,
        url=resource_dict.get("url"),
        code=resource_dict.get("code")
    )
    await new_resource.insert()
    await new_resource.fetch_all_links()
    
    return await _resource_doc_to_model(new_resource)

@router.get("", response_model=ResourceCollection)
async def list_resources(
    _current_user: User = Depends(get_current_user)
):
    resources = await Resource.find_all().to_list()
    await asyncio.gather(*[resource.fetch_all_links() for resource in resources])
    processed_resources = await asyncio.gather(*[_resource_doc_to_model(resource) for resource in resources])
    return ResourceCollection(resources=processed_resources)

@router.get("/user/{user_id}", response_model=ResourceCollection)
async def get_resources_by_user(
    user_id: str,
    _current_user: User = Depends(get_current_user)
):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resources = await Resource.find(Resource.user == user).to_list()
    await asyncio.gather(*[resource.fetch_all_links() for resource in resources])
    processed_resources = await asyncio.gather(*[_resource_doc_to_model(resource) for resource in resources])
    return ResourceCollection(resources=processed_resources)

async def _resource_doc_to_model(resource: Resource) -> ResourceModel:
    from models.resource import (
        ArticleResource, CodeSnippetResource, BookResource, CourseResource
    )
    from models.user import UserResponse
    from models.tag import TagModel
    
    user_response = UserResponse(
        id=str(resource.user.id),
        first_name=resource.user.first_name,
        last_name=resource.user.last_name,
        email=resource.user.email
    )
    
    tags = [
        TagModel(id=str(tag.id), name=tag.name)
        for tag in resource.tags
    ]
    
    base_data = {
        "id": str(resource.id),
        "title": resource.title,
        "description": resource.description,
        "user": user_response,
        "tags": tags
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
