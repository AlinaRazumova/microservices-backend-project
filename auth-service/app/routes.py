from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import UserRegister, UserLogin, UserResponse, TokenResponse, RoleUpdate
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

router = APIRouter()
security = HTTPBearer()


def error_response(code: str, message: str, details: str | None = None):
    return {
        "code": code,
        "message": message,
        "details": details,
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_TOKEN",
                "Token is invalid or expired",
            ),
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_TOKEN",
                "Token does not contain user id",
            ),
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "USER_NOT_FOUND",
                "User from token does not exist",
            ),
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(
                "FORBIDDEN",
                "Only admin can perform this action",
            ),
        )

    return current_user


@router.post("/auth/register", response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == user_data.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                "EMAIL_ALREADY_EXISTS",
                "User with this email already exists",
            ),
        )

    existing_username = db.query(User).filter(User.username == user_data.username).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                "USERNAME_ALREADY_EXISTS",
                "User with this username already exists",
            ),
        )

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/auth/login", response_model=TokenResponse)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_CREDENTIALS",
                "Invalid email or password",
            ),
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_CREDENTIALS",
                "Invalid email or password",
            ),
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                "USER_NOT_FOUND",
                "User not found",
            ),
        )

    if current_user.role != "admin" and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(
                "FORBIDDEN",
                "You can view only your own profile",
            ),
        )

    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    allowed_roles = ["user", "admin", "manager"]

    if role_data.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                "INVALID_ROLE",
                "Role must be one of: user, admin, manager",
            ),
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                "USER_NOT_FOUND",
                "User not found",
            ),
        )

    user.role = role_data.role
    db.commit()
    db.refresh(user)

    return user