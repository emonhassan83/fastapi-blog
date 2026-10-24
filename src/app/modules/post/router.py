from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.post.schemas import PostCreate, PostRead, PostUpdate
from app.modules.post.service import PostService

router = APIRouter()
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: DatabaseSession) -> dict:
    post = PostService(db).create_post(post_data)
    return {
        "message": "Post created successfully",
        "data": PostRead.model_validate(post).model_dump(),
    }


@router.get("")
def get_posts(db: DatabaseSession) -> dict:
    posts = PostService(db).list_posts()
    return {
        "message": "Posts retrieved successfully",
        "data": [PostRead.model_validate(post).model_dump() for post in posts],
    }


@router.get("/{post_id}")
def get_post(post_id: int, db: DatabaseSession) -> dict:
    post = PostService(db).get_post(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return {
        "message": "Post retrieved successfully",
        "data": PostRead.model_validate(post).model_dump(),
    }


@router.put("/{post_id}")
def update_post(post_id: int, post_data: PostUpdate, db: DatabaseSession) -> dict:
    post = PostService(db).update_post(post_id, post_data)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return {
        "message": "Post updated successfully",
        "data": PostRead.model_validate(post).model_dump(),
    }


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DatabaseSession) -> Response:
    if not PostService(db).delete_post(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
