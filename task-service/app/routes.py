import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .models import AuditLog, Task
from .schemas import AuditLogResponse, TaskAssign, TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger("task-service")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")

ALLOWED_STATUSES = ["todo", "in_progress", "done", "cancelled"]
ALLOWED_PRIORITIES = ["low", "medium", "high"]


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
            detail=error_response(
                "AUTH_SERVICE_UNAVAILABLE",
                "Auth Service is not available for token validation",
            ),
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response("INVALID_TOKEN", "Token is invalid or expired"),
        )

    user = response.json()
    return {"id": int(user["id"]), "role": user["role"], "username": user.get("username")}


def validate_status(task_status: str):
    if task_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("INVALID_STATUS", "Status must be one of: todo, in_progress, done, cancelled"),
        )


def validate_priority(priority: str):
    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response("INVALID_PRIORITY", "Priority must be one of: low, medium, high"),
        )


def get_task_or_404(task_id: int, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response("TASK_NOT_FOUND", "Task not found"),
        )
    return task


def can_manage_all_tasks(current_user: dict):
    return current_user["role"] in ["admin", "manager"]


def check_task_access(task: Task, current_user: dict):
    if can_manage_all_tasks(current_user):
        return
    if task.owner_id == current_user["id"]:
        return
    if task.assigned_to == current_user["id"]:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_response("FORBIDDEN", "You do not have access to this task"),
    )


def require_task_assignment_permission(current_user: dict):
    if not can_manage_all_tasks(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("FORBIDDEN", "Only admin or manager can assign tasks to other users"),
        )


def create_notification(user_id: int | None, task_id: int, title: str, message: str):
    if user_id is None:
        return
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post(
                f"{NOTIFICATION_SERVICE_URL}/internal/notifications",
                json={"user_id": user_id, "task_id": task_id, "title": title, "message": message},
            )
    except Exception as exc:
        logger.warning("Notification Service is not available: %s", exc)


def unique_recipients(*user_ids: int | None) -> list[int]:
    recipients = []
    for user_id in user_ids:
        if user_id is not None and user_id not in recipients:
            recipients.append(user_id)
    return recipients


def notify_many(user_ids: list[int], task_id: int, title: str, message: str):
    for user_id in user_ids:
        create_notification(user_id, task_id, title, message)


def write_audit_log(db: Session, actor_id: int, action: str, task_id: int | None = None, details: str | None = None):
    audit_log = AuditLog(task_id=task_id, actor_id=actor_id, action=action, details=details)
    db.add(audit_log)


@router.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Task)

    if not can_manage_all_tasks(current_user):
        query = query.filter((Task.owner_id == current_user["id"]) | (Task.assigned_to == current_user["id"]))

    if status_filter is not None:
        validate_status(status_filter)
        query = query.filter(Task.status == status_filter)

    if priority_filter is not None:
        validate_priority(priority_filter)
        query = query.filter(Task.priority == priority_filter)

    if search:
        pattern = f"%{search}%"
        query = query.filter((Task.title.ilike(pattern)) | (Task.description.ilike(pattern)))

    return query.order_by(Task.id.asc()).all()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_or_404(task_id, db)
    check_task_access(task, current_user)
    return task


@router.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    validate_status(task_data.status)
    validate_priority(task_data.priority)

    if task_data.assigned_to is not None and not can_manage_all_tasks(current_user):
        require_task_assignment_permission(current_user)

    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        deadline=task_data.deadline,
        owner_id=current_user["id"],
        assigned_to=task_data.assigned_to,
    )

    db.add(task)
    db.flush()
    write_audit_log(db, current_user["id"], "TASK_CREATED", task.id, f"Task '{task.title}' was created")
    db.commit()
    db.refresh(task)

    # Personal notifications:
    # - if a user creates a private task, only the creator gets a notification;
    # - if admin/manager creates and assigns a task, both creator and assigned user are notified.
    create_notification(task.owner_id, task.id, "Task created", f"Task '{task.title}' was created.")
    if task.assigned_to and task.assigned_to != task.owner_id:
        create_notification(task.assigned_to, task.id, "Task assigned to you", f"Task '{task.title}' was assigned to you.")

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_or_404(task_id, db)
    check_task_access(task, current_user)

    old_status = task.status
    old_priority = task.priority
    old_deadline = task.deadline
    old_assigned_to = task.assigned_to
    update_data = task_data.model_dump(exclude_unset=True)

    if "status" in update_data:
        validate_status(update_data["status"])
    if "priority" in update_data:
        validate_priority(update_data["priority"])
    if "assigned_to" in update_data and not can_manage_all_tasks(current_user):
        require_task_assignment_permission(current_user)

    changed_fields = []
    for field, value in update_data.items():
        old_value = getattr(task, field)
        if old_value != value:
            changed_fields.append(f"{field}: {old_value} -> {value}")
        setattr(task, field, value)

    if changed_fields:
        write_audit_log(db, current_user["id"], "TASK_UPDATED", task.id, "; ".join(changed_fields))

    db.commit()
    db.refresh(task)

    if changed_fields:
        recipients = unique_recipients(task.owner_id, task.assigned_to, current_user["id"])

        if "assigned_to" in update_data and old_assigned_to != task.assigned_to and task.assigned_to is not None:
            create_notification(task.assigned_to, task.id, "Task assigned to you", f"Task '{task.title}' was assigned to you.")

        if "status" in update_data and old_status != task.status:
            notify_many(recipients, task.id, "Task status changed", f"Task '{task.title}' status changed from {old_status} to {task.status}.")
        elif "deadline" in update_data and old_deadline != task.deadline:
            notify_many(recipients, task.id, "Task deadline changed", f"Task '{task.title}' deadline was changed.")
        elif "priority" in update_data and old_priority != task.priority:
            notify_many(recipients, task.id, "Task priority changed", f"Task '{task.title}' priority changed from {old_priority} to {task.priority}.")
        else:
            notify_many(recipients, task.id, "Task updated", f"Task '{task.title}' was updated.")

    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_or_404(task_id, db)

    if current_user["role"] != "admin" and task.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("FORBIDDEN", "Only task owner or admin can delete this task"),
        )

    recipients = unique_recipients(task.owner_id, task.assigned_to, current_user["id"])
    notify_many(recipients, task.id, "Task deleted", f"Task '{task.title}' was deleted.")

    write_audit_log(db, current_user["id"], "TASK_DELETED", task.id, f"Task '{task.title}' was deleted")
    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


@router.put("/tasks/{task_id}/assign", response_model=TaskResponse)
def assign_task(task_id: int, assign_data: TaskAssign, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_or_404(task_id, db)
    require_task_assignment_permission(current_user)

    old_assigned_to = task.assigned_to
    task.assigned_to = assign_data.assigned_to
    write_audit_log(db, current_user["id"], "TASK_ASSIGNED", task.id, f"assigned_to: {old_assigned_to} -> {assign_data.assigned_to}")

    db.commit()
    db.refresh(task)

    recipients = unique_recipients(task.owner_id, task.assigned_to, current_user["id"])
    notify_many(recipients, task.id, "Task assignment changed", f"Task '{task.title}' assignment changed from User #{old_assigned_to or '-'} to User #{task.assigned_to or '-'}.")

    return task


@router.get("/tasks/{task_id}/history", response_model=list[AuditLogResponse])
def get_task_history(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = get_task_or_404(task_id, db)
    check_task_access(task, current_user)
    return db.query(AuditLog).filter(AuditLog.task_id == task_id).order_by(AuditLog.created_at.desc()).all()


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Global audit log is an administrative/managerial view.
    # Regular users can still access history of their own/assigned tasks via /tasks/{task_id}/history.
    if not can_manage_all_tasks(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response("FORBIDDEN", "Only admin or manager can access global audit logs"),
        )

    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
