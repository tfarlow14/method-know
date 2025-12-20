from fastapi import APIRouter, HTTPException, Body, status, Depends
from datetime import datetime
from models.resource import ResourceModel, ResourceModelInput, ResourceCollection
from models.user import User
from utils.auth import get_current_user
from services import dynamodb
import asyncio

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", response_model=ResourceModel, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceModelInput = Body(...),
    current_user: User = Depends(get_current_user)
):
    resource_dict = resource.model_dump(exclude=["tag_ids"])
    
    # Validate tags exist
    if resource.tag_ids:
        tag_items = await dynamodb.get_tags_by_ids(resource.tag_ids)
        if len(tag_items) != len(resource.tag_ids):
            found_ids = {tag['tag_id'] for tag in tag_items}
            missing_ids = [tid for tid in resource.tag_ids if tid not in found_ids]
            raise HTTPException(status_code=400, detail=f"Tags {missing_ids} do not exist")
    
    # Create resource data
    resource_data = {
        'title': resource_dict['title'],
        'description': resource_dict['description'],
        'type': resource_dict['type'],
        'user_id': current_user.user_id,
        'tag_ids': resource.tag_ids,
    }
    
    # Add optional fields based on type
    if 'url' in resource_dict:
        resource_data['url'] = resource_dict['url']
    if 'code' in resource_dict:
        resource_data['code'] = resource_dict['code']
    if 'author' in resource_dict:
        resource_data['author'] = resource_dict['author']
    
    resource_item = await dynamodb.create_resource(resource_data)
    return await _resource_item_to_model(resource_item)

@router.get("", response_model=ResourceCollection)
async def list_resources(
    _current_user: User = Depends(get_current_user)
):
    resource_items = await dynamodb.list_resources()
    processed_resources = await asyncio.gather(*[_resource_item_to_model(item) for item in resource_items])
    return ResourceCollection(resources=processed_resources)

@router.get("/user/{user_id}", response_model=ResourceCollection)
async def get_resources_by_user(
    user_id: str,
    _current_user: User = Depends(get_current_user)
):
    user_item = await dynamodb.get_user_by_id(user_id)
    if not user_item:
        raise HTTPException(status_code=404, detail="User not found")
    
    resource_items = await dynamodb.get_resources_by_user_id(user_id)
    processed_resources = await asyncio.gather(*[_resource_item_to_model(item) for item in resource_items])
    return ResourceCollection(resources=processed_resources)

@router.put("/{resource_id}", response_model=ResourceModel)
async def update_resource(
    resource_id: str,
    resource: ResourceModelInput = Body(...),
    current_user: User = Depends(get_current_user)
):
    existing_resource_item = await dynamodb.get_resource_by_id(resource_id)
    if not existing_resource_item:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if user owns the resource
    if existing_resource_item['user_id'] != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only update your own resources")
    
    resource_dict = resource.model_dump(exclude=["tag_ids"])
    
    # Validate tags exist
    if resource.tag_ids:
        tag_items = await dynamodb.get_tags_by_ids(resource.tag_ids)
        if len(tag_items) != len(resource.tag_ids):
            found_ids = {tag['tag_id'] for tag in tag_items}
            missing_ids = [tid for tid in resource.tag_ids if tid not in found_ids]
            raise HTTPException(status_code=400, detail=f"Tags {missing_ids} do not exist")
    
    # Update resource fields
    update_data = {
        'title': resource_dict['title'],
        'description': resource_dict['description'],
        'type': resource_dict['type'],
        'tag_ids': resource.tag_ids,
    }
    
    # Add optional fields
    if 'url' in resource_dict:
        update_data['url'] = resource_dict['url']
    if 'code' in resource_dict:
        update_data['code'] = resource_dict['code']
    if 'author' in resource_dict:
        update_data['author'] = resource_dict['author']
    
    updated_resource_item = await dynamodb.update_resource(resource_id, update_data)
    return await _resource_item_to_model(updated_resource_item)

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user)
):
    existing_resource_item = await dynamodb.get_resource_by_id(resource_id)
    if not existing_resource_item:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if user owns the resource
    if existing_resource_item['user_id'] != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own resources")
    
    await dynamodb.delete_resource(resource_id)
    return None

async def _resource_item_to_model(resource_item: dict) -> ResourceModel:
    """Convert DynamoDB resource item to ResourceModel with denormalized user and tags."""
    from models.resource import (
        ArticleResource, CodeSnippetResource, BookResource, CourseResource
    )
    from models.user import UserResponse
    from models.tag import TagModel
    
    # Fetch user
    user_item = await dynamodb.get_user_by_id(resource_item['user_id'])
    if not user_item:
        raise HTTPException(status_code=404, detail="User not found for resource")
    
    user_response = UserResponse(
        id=user_item['user_id'],
        first_name=user_item['first_name'],
        last_name=user_item['last_name'],
        email=user_item['email']
    )
    
    # Fetch tags
    tag_items = []
    if resource_item.get('tag_ids'):
        tag_items = await dynamodb.get_tags_by_ids(resource_item['tag_ids'])
    
    tags = [
        TagModel(id=tag['tag_id'], name=tag['name'])
        for tag in tag_items
    ]
    
    # Parse created_at
    created_at = None
    if 'created_at' in resource_item:
        try:
            created_at = datetime.fromisoformat(resource_item['created_at'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            pass
    
    base_data = {
        "id": resource_item['resource_id'],
        "title": resource_item['title'],
        "description": resource_item['description'],
        "user": user_response,
        "tags": tags,
        "created_at": created_at
    }
    
    resource_type = resource_item['type']
    if resource_type == "article":
        return ArticleResource(**base_data, url=resource_item.get('url', ''))
    elif resource_type == "code_snippet":
        return CodeSnippetResource(**base_data, code=resource_item.get('code', ''))
    elif resource_type == "book":
        return BookResource(**base_data, author=resource_item.get('author'))
    elif resource_type == "course":
        return CourseResource(**base_data, author=resource_item.get('author'))
    else:
        raise ValueError(f"Unknown resource type: {resource_type}")
