import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Notification
from .schemas import NotificationCreate, NotificationResponse

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger("notification-service")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")


def error_response(code: str, message: str, details: str | None = None):
    return {"code": code, "message": message, "details": details}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(
                f"{AUTH_SERVICE_URL}/internal/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.RequestError as exc:
        logger.error("Auth Service is not available: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_response("AUTH_SERVICE_UNAVAILABLE", "Auth Service is not available for token validation"),
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("INVALID_TOKEN", "Token is invalid or expired"),
        )

    user = response.json()
    return {"id": int(user["id"]), "role": user["role"], "username": user.get("username")}


@router.post("/internal/notifications", response_model=NotificationResponse)
def create_internal_notification(notification_data: NotificationCreate, db: Session = Depends(get_db)):
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
def get_notifications(unread_only: bool = False, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Notifications are personal: every role sees only notifications addressed to the current user.
    # Admin and manager can inspect all tasks/audit logs in Task Service, but their notification inbox
    # should not be polluted by private notifications of all users.
    query = db.query(Notification).filter(Notification.user_id == current_user["id"])

    if unread_only:
        query = query.filter(Notification.is_read.is_(False))

    return query.order_by(Notification.created_at.desc()).all()


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("NOTIFICATION_NOT_FOUND", "Notification not found"),
        )

    if notification.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("FORBIDDEN", "You cannot access this notification"),
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification
