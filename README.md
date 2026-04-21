# microservices-backend-project
Academic project: microservices-based system with REST API, authentication, database, Docker, and web/mobile client.

## Project Status

Initial version prepared for academic project submission.

# Microservices Backend Project

Project for academic submission: cloud-based task management system built in microservices architecture with AWS in mind.

## Current progress

Initial project structure has been prepared:

- Auth Service created with FastAPI
- Task Service created with FastAPI
- Dockerfiles added for both services
- docker-compose added with PostgreSQL
- documentation folder prepared

## Architecture

The system is based on two main microservices:

- **Auth Service** – user registration, login, JWT authentication, role management
- **Task Service** – task CRUD operations, assignment, status, priority, deadlines

## Technology stack

- Python
- FastAPI
- PostgreSQL
- Docker / Docker Compose
- React (planned frontend)
- AWS (planned deployment)

## Run locally

```bash
docker-compose up --build
