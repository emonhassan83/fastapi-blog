from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DatabaseSession
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.user.schemas import UserRead, UserResponse

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Login to obtain JWT access token",
)
def login(login_data: LoginRequest, db: DatabaseSession) -> TokenResponse:
    """Authenticate with user email and password, returning signed JWT access token."""
    return AuthService(db).login(login_data)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(current_user: CurrentUser) -> UserResponse:
    """Fetch current user profile using Bearer JWT token."""
    return UserResponse(
        message="Current user profile retrieved successfully",
        data=UserRead.model_validate(current_user),
    )
