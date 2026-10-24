from random import randrange

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

router = APIRouter()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


class UpdatePost(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


posts: list[dict] = [
    {
        "id": 1,
        "title": "First Post",
        "content": "This is the content of the first post.",
        "published": True,
        "rating": 5,
    },
    {
        "id": 2,
        "title": "Second Post",
        "content": "This is the content of the second post.",
        "published": True,
        "rating": 4,
    },
]


@router.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Hello from fastapi-blog!"}


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post) -> dict:
    new_post = post.model_dump()
    new_post["id"] = randrange(0, 1_000_000)
    posts.append(new_post)
    return {"message": "Post created successfully", "data": new_post}


@router.get("/posts")
def get_posts() -> dict:
    return {"message": "Posts retrieved successfully", "data": posts}


@router.get("/posts/{id}")
def get_post(id: int) -> dict:
    post = next((post for post in posts if post["id"] == id), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    return {"message": "Post retrieved successfully", "data": post}


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int) -> Response:
    index = next((i for i, post in enumerate(posts) if post["id"] == id), None)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/posts/{id}")
def update_post(id: int, updated_post: UpdatePost) -> dict:
    index = next((i for i, post in enumerate(posts) if post["id"] == id), None)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )

    posts[index] = {**posts[index], **updated_post.model_dump()}
    return {"message": "Post updated successfully", "data": posts[index]}
