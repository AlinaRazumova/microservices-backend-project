# AGENTS.md

This project is based on a microservices architecture. Each service is responsible for a specific business area of the system.

## Microservices

### Auth Service
Responsible for user identity and access management:
- user registration
- user login
- JWT token generation and validation
- authorization for protected endpoints
- user role assignment and verification

### Task Service
Responsible for task management:
- creating tasks
- retrieving task list and task details
- updating tasks
- deleting tasks
- assigning tasks to users
- managing status, priority and deadlines
- filtering and searching tasks

### Notification Service (optional)
Optional service planned as a future extension:
- notifications about task assignment
- notifications about task status changes
- reminders about approaching deadlines

## Communication

- The client communicates with the system through REST API
- Microservices communicate with each other via HTTP REST
- Authentication and authorization are based on JWT tokens
- Only microservices can communicate with the database
- The client does not access the database directly

## Notes

Each microservice is developed independently and exposes well-defined interfaces.
The current MVP focuses mainly on Auth Service and Task Service.
Notification Service is treated as an optional extension.
