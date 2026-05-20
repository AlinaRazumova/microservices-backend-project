# Architecture

The project is designed as a microservices-based task management system.

## Main Components

### React Client

The web client is a simple React application used to demonstrate the main user flow:

- registration
- login
- task creation
- task list
- task filtering and searching
- status update
- task deletion
- notifications

The client communicates only with REST APIs. It does not connect directly to the database.

### Auth Service

Responsible for authentication and user management:

- user registration
- user login
- password hashing
- JWT generation
- JWT validation
- current user endpoint
- role management

### Task Service

Responsible for task management:

- create task
- list tasks
- task details
- update task
- delete task
- assign task
- filter by status and priority
- search by title and description

### Notification Service

Responsible for notifications:

- receive internal notification events
- list user notifications
- mark notifications as read

### PostgreSQL

A relational database is used for persistent storage. Only backend services communicate with PostgreSQL.

## Communication

```text
React Client
    |
    | HTTP REST API
    v
Auth Service       Task Service       Notification Service
    |                   |                     |
    | SQLAlchemy        | SQLAlchemy          | SQLAlchemy
    v                   v                     v
PostgreSQL database environment
```

Task Service can also send internal HTTP requests to Notification Service when a task is created, assigned or updated.

## Authorization

The system uses JWT access tokens.

1. User logs in through Auth Service.
2. Auth Service returns JWT token.
3. Client sends token in the `Authorization` header.
4. Task Service and Notification Service validate the token using the same secret key.
5. Services use user id and role from the token to protect resources.

## Roles

Supported roles:

- `user`
- `manager`
- `admin`

The first registered user becomes `admin` automatically.

## Error Format

All services use a consistent error response format:

```json
{
  "code": "ERROR_CODE",
  "message": "Description of the error",
  "details": "Optional additional information"
}
```
