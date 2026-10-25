from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import DatabaseSession, PaginationDep
from app.modules.post.schemas import (
    PostCreate,
    PostListResponse,
    PostRead,
    PostResponse,
    PostUpdate,
)
from app.modules.post.service import PostService
from app.shared.pagination import PaginationMeta

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post_data: PostCreate, db: DatabaseSession) -> PostResponse:
    post = PostService(db).create_post(post_data)
    return PostResponse(
        message="Post created successfully",
        data=PostRead.model_validate(post),
    )


@router.get("", response_model=PostListResponse)
def get_posts(
    db: DatabaseSession,
    pagination: PaginationDep,
) -> PostListResponse:
    posts, total = PostService(db).list_posts(
        page=pagination.page, limit=pagination.limit
    )
    return PostListResponse(
        message="Posts retrieved successfully",
        data=[PostRead.model_validate(post) for post in posts],
        pagination=PaginationMeta.create(
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        ),
    )



@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: DatabaseSession) -> PostResponse:
    post = PostService(db).get_post(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return PostResponse(
        message="Post retrieved successfully",
        data=PostRead.model_validate(post),
    )


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: DatabaseSession) -> PostResponse:
    post = PostService(db).update_post(post_id, post_data)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return PostResponse(
        message="Post updated successfully",
        data=PostRead.model_validate(post),
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DatabaseSession) -> Response:
    if not PostService(db).delete_post(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
