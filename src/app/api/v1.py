from fastapi import APIRouter

from app.modules.post.router import router as post_router
from app.modules.user.router import router as user_router

router = APIRouter()
router.include_router(post_router, prefix="/posts", tags=["Posts"])
router.include_router(user_router, prefix="/users", tags=["Users"])

