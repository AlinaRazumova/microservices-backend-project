# AGENTS.md

This project is based on a microservices architecture, where each service is responsible for a specific part of the system.

## Services (Agents)

### Auth Service
Handles user authentication and authorization:
- user registration
- user login
- JWT token generation and validation
- role management

### Task Service
Handles task management:
- creating tasks
- retrieving tasks
- updating tasks
- deleting tasks
- assigning tasks to users
- managing task status, priority and deadlines

### Notification Service (optional)
Handles system notifications:
- notifications about task assignment
- notifications about status changes
- reminders about deadlines

## Communication

- Client communicates with services via REST API
- Services communicate with each other via HTTP REST
- Authentication is handled using JWT tokens

## Notes

Each service is developed independently and communicates through well-defined interfaces.
