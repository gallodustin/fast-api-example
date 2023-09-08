from random import randrange

from fastapi import FastAPI, HTTPException, Response, status
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print('Database connection was successful.')
except Exception as e:
    print(f'Database connection failed: {e}')
    
@app.get('/')
def root():
    return {'message': 'Miami is nice'}

@app.get('/posts')
def get_posts():
    cursor.execute('SELECT * FROM posts;')
    posts = cursor.fetchall()
    return {'data': posts}

@app.get('/posts/{id}')
def get_post(id: int):
    cursor.execute('SELECT * FROM posts WHERE id = %s;', (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post {id} was not found.')
    return {'data': post}

@app.post('/posts')
def create_posts(post: Post, status_code=status.HTTP_201_CREATED):
    # passing as f string here would be bad because it allows sql injection
    # cursor.execute() checks for this before doing the substitution
    cursor.execute('INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;', (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit() # otherwise the changes won't persist in the DB
    return {'data': new_post}

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute('DELETE FROM posts WHERE id = %s RETURNING *;', (str(id),))
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute('UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;', (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    conn.commit()
    return {'message': 'post updated.', 'data': updated_post}