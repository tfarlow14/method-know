from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TagModel(BaseModel):
    """Pydantic model for tag creation/updates"""
    id: Optional[str] = Field(default=None)
    name: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class Tag(BaseModel):
    """Tag model for DynamoDB"""
    tag_id: str
    name: str
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> "Tag":
        """Create Tag from DynamoDB item."""
        return cls(
            tag_id=item.get('tag_id', ''),
            name=item.get('name', '')
        )
    
    def to_dynamodb_item(self) -> dict:
        """Convert Tag to DynamoDB item."""
        return {
            'tag_id': self.tag_id,
            'name': self.name
        }
    
    @property
    def id(self) -> str:
        """Alias for tag_id for compatibility."""
        return self.tag_id

class TagCollection(BaseModel):
    tags: list[TagModel]
