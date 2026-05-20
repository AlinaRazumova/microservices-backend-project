import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .models import Notification
from .schemas import NotificationCreate, NotificationResponse

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def error_response(code: str, message: str, details: str | None = None):
    return {"code": code, "message": message, "details": details}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("INVALID_TOKEN", "Token is invalid or expired"),
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("INVALID_TOKEN", "Token does not contain user id"),
        )

    return {"id": int(user_id), "role": role}


@router.post("/internal/notifications", response_model=NotificationResponse)
def create_internal_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
):
    notification = Notification(
        user_id=notification_data.user_id,
        task_id=notification_data.task_id,
        title=notification_data.title,
        message=notification_data.message,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


@router.get("/notifications", response_model=list[NotificationResponse])
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Notification)

    if current_user["role"] != "admin":
        query = query.filter(Notification.user_id == current_user["id"])

    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    return query.order_by(Notification.created_at.desc()).all()


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("NOTIFICATION_NOT_FOUND", "Notification not found"),
        )

    if current_user["role"] != "admin" and notification.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("FORBIDDEN", "You cannot access this notification"),
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification
