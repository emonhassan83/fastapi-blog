from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.post.router import router as post_router
from app.modules.user.router import router as user_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(post_router, prefix="/posts", tags=["Posts"])
router.include_router(user_router, prefix="/users", tags=["Users"])
