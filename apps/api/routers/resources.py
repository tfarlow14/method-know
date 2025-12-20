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
        code=resource_dict.get("code"),
        author=resource_dict.get("author")
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

@router.put("/{resource_id}", response_model=ResourceModel)
async def update_resource(
    resource_id: str,
    resource: ResourceModelInput = Body(...),
    current_user: User = Depends(get_current_user)
):
    existing_resource = await Resource.get(resource_id)
    if not existing_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Fetch the user link to ensure it's loaded
    await existing_resource.fetch_all_links()
    
    # Check if user owns the resource
    if str(existing_resource.user.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only update your own resources")
    
    resource_dict = resource.model_dump(exclude=["tag_ids"])
    
    # Update tags
    tag_links = []
    if resource.tag_ids:
        tags = await asyncio.gather(*[Tag.get(tag_id) for tag_id in resource.tag_ids])
        for i, tag in enumerate(tags):
            if not tag:
                raise HTTPException(status_code=400, detail=f"Tag {resource.tag_ids[i]} does not exist")
        tag_links = tags
    
    # Update resource fields
    existing_resource.title = resource_dict["title"]
    existing_resource.description = resource_dict["description"]
    existing_resource.type = resource_dict["type"]
    existing_resource.tags = tag_links
    existing_resource.url = resource_dict.get("url")
    existing_resource.code = resource_dict.get("code")
    existing_resource.author = resource_dict.get("author")
    
    await existing_resource.save()
    await existing_resource.fetch_all_links()
    
    return await _resource_doc_to_model(existing_resource)

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user)
):
    existing_resource = await Resource.get(resource_id)
    if not existing_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Fetch the user link to ensure it's loaded
    await existing_resource.fetch_all_links()
    
    # Check if user owns the resource
    if str(existing_resource.user.id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only delete your own resources")
    
    await existing_resource.delete()
    return None

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
        "tags": tags,
        "created_at": resource.created_at
    }
    
    if resource.type == "article":
        return ArticleResource(**base_data, url=resource.url or "")
    elif resource.type == "code_snippet":
        return CodeSnippetResource(**base_data, code=resource.code or "")
    elif resource.type == "book":
        return BookResource(**base_data, author=resource.author)
    elif resource.type == "course":
        return CourseResource(**base_data, author=resource.author)
    else:
        raise ValueError(f"Unknown resource type: {resource.type}")
