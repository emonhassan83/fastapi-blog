from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.post.models import PostRecord
from app.modules.post.schemas import PostCreate, PostUpdate


class PostRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, post_data: PostCreate) -> PostRecord:
        post = PostRecord(**post_data.model_dump())
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post

    def get_all(self) -> list[PostRecord]:
        return list(self.session.scalars(select(PostRecord)).all())

    def get_by_id(self, post_id: int) -> PostRecord | None:
        return self.session.get(PostRecord, post_id)

    def update(self, post: PostRecord, post_data: PostUpdate) -> PostRecord:
        for field, value in post_data.model_dump().items():
            setattr(post, field, value)
        self.session.commit()
        self.session.refresh(post)
        return post

    def delete(self, post: PostRecord) -> None:
        self.session.delete(post)
        self.session.commit()
