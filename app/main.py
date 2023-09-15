from typing import List

import psycopg2
from fastapi import Depends, FastAPI, HTTPException, Response, status
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

try:
    # in a real app you shouldn't hardcode this
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='postgres', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print('Database connection was successful.')
except Exception as e:
    print(f'Database connection failed: {e}')
    
@app.get('/')
def root():
    return {'message': 'Miami is nice'}

@app.get('/posts', response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute('SELECT * FROM posts;')
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts

@app.get('/posts/{id}', response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute('SELECT * FROM posts WHERE id = %s;', (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post {id} was not found.')
    return post

@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # passing as f string here would be bad because it allows sql injection
    # cursor.execute() checks for this before doing the substitution
    # cursor.execute('INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;', (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit() # otherwise the changes won't persist in the DB
    new_post = models.Post(**post.model_dump())
    db.add(new_post) # add the new post to the session
    db.commit() # commit the session to the DB
    db.refresh(new_post) # refresh the session to get the new post
    return new_post

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute('DELETE FROM posts WHERE id = %s RETURNING *;', (str(id),))
    # deleted_post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    # conn.commit()
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute('UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;', (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    updated_post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = updated_post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post {id} was not found.')
    # conn.commit()
    updated_post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return updated_post

@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password
    user.password = pwd_context.hash(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user) # add the new post to the session
    db.commit() # commit the session to the DB
    db.refresh(new_user) # refresh the session to get the new user
    return new_user