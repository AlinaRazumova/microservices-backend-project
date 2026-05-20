# Microservices Backend Project

Cloud-based task management system designed in a microservices architecture with AWS deployment in mind.

The project implements a working backend MVP for a task management system. It includes authentication, JWT-based authorization, user roles, task CRUD, task assignment, filtering, searching, notifications, PostgreSQL integration, Docker Compose environment, Swagger/OpenAPI documentation and a simple React web client.

## Project Goal

The goal of the project is to design and implement a cloud-based task management system for individual users and small teams.

The system supports user authentication, role-based access control, task management and basic CRUD operations through REST API. The architecture is based on separated backend services communicating through HTTP REST APIs.

## Implemented MVP Features

- user registration
- user login
- JWT-based authentication
- protected endpoints using access tokens
- role-based access control
- administrator role management
- creating tasks
- viewing task list and task details
- editing tasks
- deleting tasks
- assigning tasks to users
- managing task status, priority and deadline
- filtering tasks by status and priority
- searching tasks by title and description
- basic notification flow for task events
- Swagger/OpenAPI documentation
- Docker Compose local environment
- simple React web client

## Architecture

The system is based on a microservices architecture.

### Auth Service

Responsible for:

- user registration
- user login
- password hashing with bcrypt
- JWT token generation
- JWT token validation
- current user information endpoint
- user data access
- role management

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
- sending basic task-event notifications to Notification Service

### Notification Service

Responsible for:

- storing notifications
- listing notifications for the current user
- marking notifications as read
- receiving internal notification events from Task Service

### React Web Client

A simple frontend client is included to demonstrate the main backend flow:

- register/login
- create tasks
- list and filter tasks
- update task status
- delete tasks
- view notifications

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

- AWS deployment planned
- GitHub Actions CI included for basic validation

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

### React Client

```text
http://localhost:3000
```

## Task Status and Priority

Allowed task statuses:

- `todo`
- `in_progress`
- `done`
- `cancelled`

Allowed task priorities:

- `low`
- `medium`
- `high`

## Error Handling

The project uses a consistent error response format for API endpoints.

Example:

```json
{
  "code": "ERROR_CODE",
  "message": "Description of the error",
  "details": "Optional additional information"
}
```

## Running the Project Locally

Create a local `.env` file from `.env.example` if needed, or use default Docker Compose values.

Start the full system:

```bash
docker compose up --build
```

Stop the system:

```bash
docker compose down
```

Reset the database volume:

```bash
docker compose down -v
```

## Example Testing Flow

1. Start the project:

```bash
docker compose up --build
```

2. Open Auth Service Swagger:

```text
http://localhost:8001/docs
```

3. Register the first user using `POST /auth/register`.

Example:

```json
{
  "email": "admin@example.com",
  "username": "admin",
  "password": "admin123"
}
```

The first user should receive:

```json
"role": "admin"
```

4. Log in using `POST /auth/login` and copy the returned `access_token`.

5. Open Task Service Swagger:

```text
http://localhost:8002/docs
```

6. Click `Authorize` and paste only the JWT token.

7. Create a task using `POST /tasks`.

8. Test task list, details, update, assignment, filtering, searching and deletion.

9. Open Notification Service Swagger:

```text
http://localhost:8003/docs
```

10. Use the same JWT token and check generated notifications with `GET /notifications`.

## Repository Structure

```text
microservices-backend-project
├── auth-service
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── task-service
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── notification-service
│   ├── app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── src
│   ├── Dockerfile
│   └── package.json
├── docs
├── .github
│   └── workflows
├── docker-compose.yml
├── .env.example
└── README.md
```

## Branching and Workflow

The project uses a pull-request based workflow.

General rules:

- no direct push to `main`
- each change should be implemented in a separate branch
- each change should be merged through a pull request
- pull requests should include a short description of implemented changes

## Project Status

Current status: backend MVP completed with additional demonstration features.

Completed:

- Auth Service implementation
- Task Service CRUD implementation
- Notification Service basic implementation
- PostgreSQL integration
- JWT-based protection
- role-based access control
- Docker Compose environment
- Swagger documentation
- simple React client
- basic CI workflow

Next possible steps:

- add automated tests
- improve production deployment configuration
- prepare AWS deployment
- connect monitoring to AWS CloudWatch
