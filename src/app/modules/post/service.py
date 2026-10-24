from sqlalchemy.orm import Session

from app.modules.post.models import PostRecord
from app.modules.post.repository import PostRepository
from app.modules.post.schemas import PostCreate, PostUpdate


class PostService:
    def __init__(self, session: Session) -> None:
        self.repository = PostRepository(session)

    def create_post(self, post_data: PostCreate) -> PostRecord:
        return self.repository.create(post_data)

    def list_posts(self) -> list[PostRecord]:
        return self.repository.get_all()

    def get_post(self, post_id: int) -> PostRecord | None:
        return self.repository.get_by_id(post_id)

    def update_post(
        self, post_id: int, post_data: PostUpdate
    ) -> PostRecord | None:
        post = self.repository.get_by_id(post_id)
        if post is None:
            return None
        return self.repository.update(post, post_data)

    def delete_post(self, post_id: int) -> bool:
        post = self.repository.get_by_id(post_id)
        if post is None:
            return False
        self.repository.delete(post)
        return True
