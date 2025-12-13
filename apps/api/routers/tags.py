from fastapi import APIRouter, Body, status, Depends
from models.tag import TagModel, Tag, TagCollection
from models.user import User
from utils.auth import get_current_user

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("", response_model=TagModel, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagModel = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Create a new tag (requires authentication)"""
    new_tag = Tag(name=tag.name)
    await new_tag.insert()
    return TagModel(name=new_tag.name)

@router.get("", response_model=TagCollection)
async def list_tags():
    """List all tags (public endpoint)"""
    tags = await Tag.find_all().to_list()
    return TagCollection(tags=[TagModel(name=tag.name) for tag in tags])
