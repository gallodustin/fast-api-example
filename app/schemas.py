from pydantic import BaseModel
from datetime import datetime

# Will be useful later as a base class for different requests using a Post
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime

    class Config: 
        orm_mode = True # so that we can use SQLAlchemy models with Pydantic which normally uses dict