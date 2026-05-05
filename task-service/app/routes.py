from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os

from .database import get_db
from .models import Task
from .schemas import TaskCreate, TaskUpdate, TaskAssign, TaskResponse

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ALLOWED_STATUSES = ["todo", "in_progress", "done", "cancelled"]
ALLOWED_PRIORITIES = ["low", "medium", "high"]


def error_response(code: str, message: str, details: str | None = None):
    return {
        "code": code,
        "message": message,
        "details": details,
    }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_TOKEN",
                "Token is invalid or expired",
            ),
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(
                "INVALID_TOKEN",
                "Token does not contain user id",
            ),
        )

    return {
        "id": int(user_id),
        "role": role,
    }


def validate_status(task_status: str):
    if task_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                "INVALID_STATUS",
                "Status must be one of: todo, in_progress, done, cancelled",
            ),
        )


def validate_priority(priority: str):
    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(
                "INVALID_PRIORITY",
                "Priority must be one of: low, medium, high",
            ),
        )


def get_task_or_404(task_id: int, db: Session):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(
                "TASK_NOT_FOUND",
                "Task not found",
            ),
        )

    return task


def check_task_access(task: Task, current_user: dict):
    if current_user["role"] == "admin":
        return

    if task.owner_id == current_user["id"]:
        return

    if task.assigned_to == current_user["id"]:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_response(
            "FORBIDDEN",
            "You do not have access to this task",
        ),
    )


@router.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    priority_filter: str | None = Query(default=None, alias="priority"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Task)

    if current_user["role"] != "admin":
        query = query.filter(
            (Task.owner_id == current_user["id"]) |
            (Task.assigned_to == current_user["id"])
        )

    if status_filter is not None:
        validate_status(status_filter)
        query = query.filter(Task.status == status_filter)

    if priority_filter is not None:
        validate_priority(priority_filter)
        query = query.filter(Task.priority == priority_filter)

    return query.all()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db)
    check_task_access(task, current_user)

    return task


@router.post("/tasks", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_status(task_data.status)
    validate_priority(task_data.priority)

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
    db.commit()
    db.refresh(task)

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db)
    check_task_access(task, current_user)

    update_data = task_data.model_dump(exclude_unset=True)

    if "status" in update_data:
        validate_status(update_data["status"])

    if "priority" in update_data:
        validate_priority(update_data["priority"])

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db)

    if current_user["role"] != "admin" and task.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(
                "FORBIDDEN",
                "Only task owner or admin can delete this task",
            ),
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
    }


@router.put("/tasks/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: int,
    assign_data: TaskAssign,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db)

    if current_user["role"] != "admin" and task.owner_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_response(
                "FORBIDDEN",
                "Only task owner or admin can assign this task",
            ),
        )

    task.assigned_to = assign_data.assigned_to

    db.commit()
    db.refresh(task)

    return task