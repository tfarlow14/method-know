from fastapi import APIRouter, Body, status, Depends
from models.tag import TagModel, Tag, TagCollection
from models.user import User
from utils.auth import get_current_user
from services import dynamodb

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("", response_model=TagModel, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagModel = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Create a new tag (requires authentication)"""
    tag_data = {'name': tag.name}
    tag_item = await dynamodb.create_tag(tag_data)
    return TagModel(id=tag_item['tag_id'], name=tag_item['name'])

@router.get("", response_model=TagCollection)
async def list_tags():
    """List all tags (public endpoint)"""
    tag_items = await dynamodb.list_tags()
    return TagCollection(tags=[TagModel(id=item['tag_id'], name=item['name']) for item in tag_items])
