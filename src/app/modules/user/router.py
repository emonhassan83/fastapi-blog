from fastapi import APIRouter, status

from app.api.deps import DatabaseSession
from app.modules.user.schemas import UserRead, UserRegister, UserResponse
from app.modules.user.service import UserService

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register a new user",
)
def register(user_data: UserRegister, db: DatabaseSession) -> UserResponse:
    user = UserService(db).register_user(user_data)
    return UserResponse(
        message="User registered successfully",
        data=UserRead.model_validate(user),
    )
