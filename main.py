from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def root():
    return {'message': 'Miami is nice'}

@app.get('/posts')
def get_posts():
    return {'data': 'Here are your posts.'}