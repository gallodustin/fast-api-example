from pydantic import BaseModel

# Will be useful later as a base class for different requests using a Post
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass
