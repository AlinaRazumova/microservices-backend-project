# Microservices Backend Project

Cloud-based task management system designed in a microservices architecture with AWS deployment in mind.

The project implements a working MVP for a task management system. It includes authentication, JWT-based authorization, user roles, task CRUD, task assignment, filtering, searching, notifications, PostgreSQL integration, Docker Compose environment, Swagger/OpenAPI documentation and a React web client.

## Project Goal

The goal of the project is to design and implement a cloud-based task management system for individual users and small teams.

The system supports user authentication, role-based access control, task management and basic CRUD operations through REST API. The architecture is based on separated backend services communicating through HTTP REST APIs.

## Implemented MVP Features

- user registration
- user login
- JWT-based authentication
- protected endpoints using access tokens
- role-based access control for `user`, `manager` and `admin`
- administrator role management
- creating tasks
- viewing task list and task details
- editing tasks
- deleting tasks
- assigning tasks to users
- managing task status, priority and deadline
- filtering tasks by status and priority
- searching tasks by title and description
- notifications for task events
- Swagger/OpenAPI documentation
- PostgreSQL database
- Docker Compose local environment
- React web client
- administrator users panel in the frontend
- task assignment through a users dropdown in the frontend
- task editing form in the frontend

## Architecture

The system is based on a microservices architecture.

```text
React frontend
      |
      | HTTP REST + JWT
      v
Auth Service        Task Service        Notification Service
      |                  |                       |
      |                  | internal HTTP          |
      v                  v                       v
                 PostgreSQL database
```

The client communicates only with backend APIs. Services use JWT tokens to protect endpoints. Task Service also sends internal notification events to Notification Service.

## Services

### Auth Service

Responsible for:

- user registration
- user login
- password hashing with bcrypt
- JWT token generation
- JWT token validation
- current user information endpoint
- user data access
- administrator role management

The first registered user automatically receives the `admin` role. All next users receive the `user` role by default. This makes the administrator workflow possible without manual database changes.

### Task Service

Responsible for:

- creating tasks
- listing tasks
- viewing task details
- updating tasks
- deleting tasks
- assigning tasks to users
- filtering tasks by status and priority
- searching tasks by title and description
- protecting task endpoints with JWT authentication
- limiting regular users to their own or assigned tasks
- sending task-event notifications to Notification Service

### Notification Service

Responsible for:

- storing notifications
- listing notifications for the current user
- marking notifications as read
- receiving internal notification events from Task Service

### React Web Client

The web client demonstrates the main system flow:

- welcome screen
- register and login
- logout
- create task
- edit task
- list and filter tasks
- update task status
- delete task
- assign task to a selected user for managers and administrators
- view notifications
- manager task coordination workflow
- admin users panel
- change user roles from the frontend

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- JWT
- bcrypt
- httpx

### Database

- PostgreSQL

### Containerization

- Docker
- Docker Compose

### Frontend

- React
- Vite

### API Documentation

- Swagger UI
- OpenAPI generated automatically by FastAPI

### Cloud / DevOps

- AWS deployment is planned as a future extension
- GitHub Actions / CI/CD can be added as a future extension

## API Overview

### Auth Service

Base URL locally:

```text
http://localhost:8001
```

Swagger:

```text
http://localhost:8001/docs
```

Available endpoints:

- `GET /`
- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /users`
- `GET /users/{user_id}`
- `PUT /users/{user_id}/role`

### Task Service

Base URL locally:

```text
http://localhost:8002
```

Swagger:

```text
http://localhost:8002/docs
```

Available endpoints:

- `GET /`
- `GET /health`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `PUT /tasks/{task_id}/assign`

Supported query parameters for `GET /tasks`:

- `status`
- `priority`
- `search`

### Notification Service

Base URL locally:

```text
http://localhost:8003
```

Swagger:

```text
http://localhost:8003/docs
```

Available endpoints:

- `GET /`
- `GET /health`
- `GET /notifications`
- `PUT /notifications/{notification_id}/read`
- `POST /internal/notifications`

The internal endpoint is used by Task Service to create notifications.

### Frontend

Local URL:

```text
http://localhost:3000
```

## Local Run

### Requirements

- Docker Desktop
- Docker Compose

### Start project

```bash
docker compose up --build
```

### Stop project

```bash
docker compose down
```

### Start from clean database

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

## Test Flow

### 1. Register first user

Open frontend:

```text
http://localhost:3000
```

Create the first account. The first registered user automatically becomes administrator.

Example:

```json
{
  "email": "admin@example.com",
  "username": "admin",
  "password": "admin123"
}
```

### 2. Login

Login with the created account. After login the dashboard is available.

### 3. Admin users panel

The administrator can:

- load users
- search users by email or username
- see user id, email, username and role
- change user role between `user`, `manager` and `admin`

Managers can load the user list for task assignment, but they cannot change user roles.

### 4. Create task

The user can create a task with:

- title
- description
- status
- priority
- deadline
- assigned user

Deadline format in the frontend:

```text
YYYY-MM-DD HH:mm
```

Example:

```text
2026-05-20 23:59
```

### 5. Assign task

The frontend uses a dropdown with existing users instead of requiring the user to manually type a technical user id.

Assignment is available only for `admin` and `manager` users. Regular users do not see the assignment field and create tasks only for themselves.

### 6. Edit task

Every task item has an `Edit` button. The edit form allows changing:

- title
- description
- status
- priority
- deadline
- assigned user

### 7. Filter and search tasks

Tasks can be filtered by:

- status
- priority

Tasks can also be searched by title or description.

### 8. Notifications

The user can load notifications and mark unread notifications as read.

## Authorization Rules

- unauthenticated requests to protected endpoints are rejected
- regular users can see only tasks they own or tasks assigned to them
- regular users do not see the task assignment field in the frontend
- regular users cannot assign tasks to other users
- regular users cannot manage user roles
- managers can see all tasks
- managers can edit task status, priority, deadline and assignment
- managers can load the user list only for task assignment
- managers cannot manage user roles
- administrators can see all tasks
- administrators can manage user roles
- administrators can assign and delete tasks

## Environment Variables

Example variables are stored in `.env.example`.

Important values:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `AUTH_DATABASE_URL`
- `TASK_DATABASE_URL`
- `NOTIFICATION_DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `NOTIFICATION_SERVICE_URL`
- `VITE_AUTH_API_URL`
- `VITE_TASK_API_URL`
- `VITE_NOTIFICATION_API_URL`

## Project Structure

```text
microservices-backend-project
├── auth-service
├── task-service
├── notification-service
├── frontend
├── docs
├── docker-compose.yml
├── README.md
├── .env.example
├── .gitignore
└── AGENTS.md
```

## Current Limitations / Future Work

The following elements are planned as future extensions and are not required for the current MVP:

- AWS deployment
- CI/CD pipeline
- advanced centralized logging
- audit log / task history
- advanced notification types
- password reset flow
- production-grade frontend routing

## Status

The current version implements the required MVP and includes additional frontend support for administrator role management, manager task coordination, user-based task assignment, task editing and notifications.


## Completed additional requirements

The project now also implements the following requirements from the proposal and optional extensions:

- **Monitoring / logging**: each FastAPI service has `/health` endpoint and request logging middleware with method, path, status code and processing time.
- **Audit log / task history**: Task Service stores task events in `audit_logs` table. It records task creation, update, assignment and deletion. Available endpoints:
  - `GET /audit-logs`
  - `GET /tasks/{task_id}/history`
- **Service-to-service REST communication**: Task Service and Notification Service validate JWT tokens through Auth Service using HTTP REST endpoint `GET /internal/auth/validate`. Task Service also communicates with Notification Service through REST to create notifications.
- **Consistent error response format**: all services include exception handlers returning errors as `{ "code": "ERROR_CODE", "message": "...", "details": ... }`.
- **Required task endpoints**: `GET /tasks/{id}` and `PUT /tasks/{id}/assign` are implemented and protected by role-based authorization.

AWS deployment and full CI/CD deployment pipeline are intentionally left as future work, while the project is prepared for container-based deployment through Docker Compose.


## Role-based behavior, notifications and audit log

The application follows a Jira/Trello-like separation between tasks, personal notifications and audit history.

- **User** sees only tasks created by them or assigned to them. A regular user cannot assign tasks to other users and does not see the global audit log.
- **Manager** sees all tasks, can assign and edit tasks, and can view the global task audit log. A manager cannot change user roles.
- **Admin** sees all tasks, manages user roles, assigns tasks and can view the global audit log.

Notifications are personal. `GET /notifications` returns only notifications addressed to the currently logged-in user, even for admin and manager accounts. Admins and managers can inspect all tasks through the task list and audit log, but their notification inbox is not filled with private notifications of all users.

The global audit log is available only to `admin` and `manager`. Regular users can access task history only for tasks they own or tasks assigned to them through `GET /tasks/{task_id}/history`.
