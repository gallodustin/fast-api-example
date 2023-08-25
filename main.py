from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

# start with some example post for now, and use memory as the "DB"
my_posts = []
my_posts.append({'title': 'title of post 1', 'content': 'content of post 1', 'id': 1})
my_posts.append({'title': 'favorite foods', 'content': 'i like pizza', 'id': 2})

@app.get('/')
def root():
    return {'message': 'Miami is nice'}

@app.get('/posts')
def get_posts():
    return {'data': my_posts}

@app.post('/posts')
def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 1000000) # this is a goofy example, but sure
    my_posts.append(post_dict)
    return {'data': post_dict}