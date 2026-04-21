from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List


app = FastAPI(
    title="Auth Service",
    description="Service responsible for user registration, login, JWT authentication and user management.",
    version="1.0.0"
)


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str


class RoleUpdateRequest(BaseModel):
    role: str


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Auth Service is running",
        "service": "auth-service",
        "version": "1.0.0"
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "auth-service"
    }


@app.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(payload: RegisterRequest):
    return {
        "message": "User registration endpoint placeholder",
        "data": {
            "username": payload.username,
            "email": payload.email
        }
    }


@app.post("/auth/login", tags=["Auth"])
def login_user(payload: LoginRequest):
    return {
        "message": "Login endpoint placeholder",
        "access_token": "demo-jwt-token",
        "token_type": "bearer",
        "user_email": payload.email
    }


@app.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user():
    return UserResponse(
        id=1,
        username="demo_user",
        email="demo@example.com",
        role="admin"
    )


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_users():
    return [
        UserResponse(
            id=1,
            username="demo_user",
            email="demo@example.com",
            role="admin"
        ),
        UserResponse(
            id=2,
            username="test_user",
            email="test@example.com",
            role="user"
        )
    ]


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user_by_id(user_id: int):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be greater than 0"
        )

    return UserResponse(
        id=user_id,
        username=f"user_{user_id}",
        email=f"user{user_id}@example.com",
        role="user"
    )


@app.put("/users/{user_id}/role", tags=["Users"])
def update_user_role(user_id: int, payload: RoleUpdateRequest):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID must be greater than 0"
        )

    allowed_roles = {"user", "admin", "manager"}
    if payload.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(sorted(allowed_roles))}"
        )

    return {
        "message": "User role update endpoint placeholder",
        "user_id": user_id,
        "new_role": payload.role
    }
