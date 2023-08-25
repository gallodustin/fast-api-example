from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
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

# don't do this lol
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get('/')
def root():
    return {'message': 'Miami is nice'}

@app.get('/posts')
def get_posts():
    return {'data': my_posts}

@app.get('/posts/{id}')
def get_post(id: int):
    found_post = find_post(id)
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    return {'post_detail': found_post}

@app.post('/posts')
def create_posts(post: Post, status_code=status.HTTP_201_CREATED):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 1000000) # this is a goofy example, but sure
    my_posts.append(post_dict)
    return {'data': post_dict}

@app.delete('/posts/{id}')
def delete_post(id: int):
    found_post = find_post(id)
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    my_posts.remove(found_post)
    return {'message': f'post {id} was deleted.'}