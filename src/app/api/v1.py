from fastapi import APIRouter

from app.modules.post.router import router as post_router

router = APIRouter()
router.include_router(post_router, prefix="/posts", tags=["Posts"])
