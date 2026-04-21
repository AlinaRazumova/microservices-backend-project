from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional


app = FastAPI(
    title="Task Service",
    description="Service responsible for task management: creating, listing, updating, deleting and assigning tasks.",
    version="1.0.0"
)


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    status: str = "new"
    priority: str = "medium"
    deadline: Optional[str] = None
    assigned_to: Optional[int] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[str] = None
    assigned_to: Optional[int] = None


class AssignTaskRequest(BaseModel):
    assigned_to: int


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    deadline: Optional[str] = None
    assigned_to: Optional[int] = None


@app.get("/", tags=["System"])
def root():

    return {
        "message": "Task Service is running",
        "service": "task-service",
        "version": "1.0.0"
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "task-service"
    }


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def get_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority_filter: Optional[str] = Query(default=None, alias="priority")
):
    tasks = [
        TaskResponse(
            id=1,
            title="Prepare architecture draft",
            description="Create initial architecture documentation",
            status="in_progress",
            priority="high",
            deadline="2026-04-25",
            assigned_to=1
        ),
        TaskResponse(
            id=2,
            title="Implement auth endpoints",
            description="Prepare register and login endpoints",
            status="new",
            priority="medium",
            deadline="2026-04-27",
            assigned_to=2
        )
    ]

    if status_filter:
        tasks = [task for task in tasks if task.status == status_filter]

    if priority_filter:
        tasks = [task for task in tasks if task.priority == priority_filter]

    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task_by_id(task_id: int):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID must be greater than 0"
        )

    return TaskResponse(
        id=task_id,
        title=f"Task {task_id}",
        description="Task details endpoint placeholder",
        status="new",
        priority="medium",
        deadline="2026-04-30",
        assigned_to=1
    )


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(payload: TaskCreateRequest):
    return TaskResponse(
        id=101,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        deadline=payload.deadline,
        assigned_to=payload.assigned_to
    )


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, payload: TaskUpdateRequest):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID must be greater than 0"
        )

    return TaskResponse(
        id=task_id,
        title=payload.title or f"Task {task_id}",
        description=payload.description or "Updated task placeholder",
        status=payload.status or "in_progress",
        priority=payload.priority or "medium",
        deadline=payload.deadline or "2026-04-30",
        assigned_to=payload.assigned_to
    )


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: int):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID must be greater than 0"
        )

    return {
        "message": "Task deleted successfully (placeholder)",
        "task_id": task_id
    }


@app.put("/tasks/{task_id}/assign", tags=["Tasks"])
def assign_task(task_id: int, payload: AssignTaskRequest):
    if task_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID must be greater than 0"
        )

    return {
        "message": "Task assignment endpoint placeholder",
        "task_id": task_id,
        "assigned_to": payload.assigned_to
    }
