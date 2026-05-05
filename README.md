# Microservices Backend Project

Cloud-based task management system designed in a microservices architecture with AWS deployment in mind.

The project has moved from the planning phase to active backend implementation.  
The current version includes working authentication, JWT-based authorization, task management functionality, PostgreSQL database integration, Docker-based local environment, and automatically generated Swagger/OpenAPI documentation.

## Project Goal

The goal of the project is to design and implement a cloud-based task management system for individual users and small teams.

The system supports user authentication, role-based access control, task management, and basic CRUD operations through REST API. The architecture is based on independent backend services that communicate through HTTP REST APIs and share a PostgreSQL database environment.

## Main Features (MVP)

Implemented and planned MVP functionality includes:

- user registration
- user login
- JWT-based authentication
- protected endpoints using access tokens
- basic role-based access control
- creating tasks
- viewing task list and task details
- editing tasks
- deleting tasks
- assigning tasks to users
- managing task status, priority, and deadline
- filtering tasks by status and priority

## Planned Extensions

Optional future extensions:

- audit log / history of changes
- notifications
- monitoring and centralized logging
- simple web client
- AWS deployment
- CI/CD pipeline

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
- basic role management

### Task Service

Responsible for:

- creating tasks
- listing tasks
- viewing task details
- updating tasks
- deleting tasks
- assigning tasks to users
- filtering tasks by status and priority
- protecting task endpoints with JWT authentication

### Optional Notification Service

Planned as a future extension of the project.

It may be responsible for notifying users about:

- task creation
- task status changes
- upcoming deadlines

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- JWT
- bcrypt

### Database

- PostgreSQL

### Containerization

- Docker
- Docker Compose

### API Documentation

- Swagger UI
- OpenAPI generated automatically by FastAPI

### Frontend

- React planned as a future client application

### Cloud / DevOps

- AWS planned
- CI/CD planned

## Current Progress

At the current stage, the following elements have been implemented:

- project repository structure
- separated `auth-service` and `task-service`
- working FastAPI application for Auth Service
- working FastAPI application for Task Service
- PostgreSQL database connection using SQLAlchemy
- user registration
- user login
- password hashing
- JWT token generation
- protected `/auth/me` endpoint
- task CRUD operations
- task assignment
- task filtering by status and priority
- Swagger/OpenAPI documentation for both services
- Dockerfiles for backend services
- `docker-compose.yml` with PostgreSQL
- `.env.example` for environment configuration
- documentation in the `docs` directory

## API Overview

### Auth Service

Available endpoints:

- `GET /`
- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /users`
- `GET /users/{id}`
- `PUT /users/{id}/role`

### Task Service

Available endpoints:

- `GET /`
- `GET /health`
- `GET /tasks`
- `GET /tasks/{id}`
- `POST /tasks`
- `PUT /tasks/{id}`
- `DELETE /tasks/{id}`
- `PUT /tasks/{id}/assign`

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