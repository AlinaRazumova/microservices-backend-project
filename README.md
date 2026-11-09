# Task Manager — Microservices Application on AWS

**Engineering thesis project | Computer Science | 2026**

A full-stack task management application built with **Python, FastAPI, React, PostgreSQL and Docker**. The application consists of three cooperating backend microservices and a React web client. It was developed and tested locally with Docker Compose and **deployed to AWS as a demonstration environment** using ECS/Fargate, ECR, RDS, Application Load Balancer and CloudWatch.

> **Status:** Implemented academic MVP. The AWS deployment was completed and verified for the engineering thesis; it is **not claimed to be continuously hosted or production-ready**.

## Features

- User registration and login, bcrypt password hashing and JWT authentication
- Role-based access control: `user`, `manager` and `admin`
- Administrator management of user roles
- Task creation, viewing, updating, deleting and assigning
- Task status, priority, deadlines, filtering and text search
- In-app personal notifications and marking notifications as read
- Audit logs and history of task operations (creation, update, assignment and deletion)
- React-based interface for users, managers and administrators
- Swagger/OpenAPI documentation, service health endpoints and request logging
- Service-to-service HTTP REST communication

The first registered account in a clean database automatically receives the `admin` role. Further accounts default to `user`.

## Architecture

| Component | Responsibility |
| --- | --- |
| **Auth Service** | Registration, login, JWT generation and validation, user accounts and roles |
| **Task Service** | Task CRUD, assignments, filtering/search and audit logs |
| **Notification Service** | Personal in-app notifications and read status |
| **React frontend** | Web client for task and user management |
| **PostgreSQL** | Stores users, tasks, audit logs and notifications |

```text
                    React + Vite frontend
                             |
                        HTTP / REST
                             |
           +-----------------+-----------------+
           |                 |                 |
      Auth Service      Task Service    Notification Service
           ^                 |                 ^
           |                 |                 |
           +-- JWT validation                 |
                             +-- task events --+
           |                 |                 |
           +-----------------+-----------------+
                             |
                         PostgreSQL
```

Task Service and Notification Service validate tokens through an internal endpoint in Auth Service. Task Service sends requests to Notification Service to create notifications when task events occur.

### Permissions

| Role | Main permissions |
| --- | --- |
| **User** | Own/assigned tasks, own notifications and history for accessible tasks |
| **Manager** | All tasks, task assignments, user list and global audit logs; no role editing |
| **Admin** | All tasks, assignments, global audit logs and user-role management |

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.11, FastAPI, Pydantic, SQLAlchemy, HTTPX |
| Security | JWT, bcrypt, role-based authorization |
| Database | PostgreSQL |
| Frontend | React, Vite, JavaScript |
| Containers | Docker, Docker Compose |
| API docs | Swagger UI, OpenAPI |
| AWS | Amazon ECR, ECS, Fargate, RDS for PostgreSQL, Application Load Balancer, CloudWatch |

## AWS deployment — completed thesis work

As part of the engineering thesis, I built Docker images for **three backend services and the frontend**, published them to four private **Amazon ECR** repositories, configured **PostgreSQL on Amazon RDS**, and launched the four application containers within **one ECS task on AWS Fargate**. An **Application Load Balancer** routed requests to the respective services using URL paths, and **CloudWatch** collected logs from the containers.

Paths such as `/auth/*`, `/users*`, `/tasks*`, `/audit-logs*` and `/notifications*` were routed to the backend services; other paths were routed to the frontend. I checked container and target-group health and service communications during the deployment.

**Deployment scope:** This was a demonstration environment with manual image publishing, a single ECS task and HTTP access. A production-grade deployment would require HTTPS/TLS, secure secret management, scaling, alerting and CI/CD. The repository does not contain a fully automated AWS provisioning pipeline.

## Local setup

**Requirements:** Docker Desktop / Docker Engine and Docker Compose.

```bash
git clone https://github.com/AlinaRazumova/microservices-backend-project.git
cd microservices-backend-project
cp .env.example .env
```

Edit `.env` and change the example credentials and `JWT_SECRET_KEY` before running the application.

```bash
docker compose up --build
```

| Component | URL | Swagger |
| --- | --- | --- |
| Frontend | http://localhost:3000 | — |
| Auth Service | http://localhost:8001 | http://localhost:8001/docs |
| Task Service | http://localhost:8002 | http://localhost:8002/docs |
| Notification Service | http://localhost:8003 | http://localhost:8003/docs |

Stop with `docker compose down`. **Warning:** `docker compose down -v` removes the local database volume and its data.

### Suggested demo flow

Register the first account (administrator), log in, create and edit tasks, change status/priority, assign a task as a manager/admin, inspect task history and notifications, and use the administrator panel to manage roles.

## API overview

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Register |
| POST | `/auth/login` | Login and obtain JWT |
| GET | `/auth/me` | Current user |
| GET | `/users` | User list (manager/admin) |
| PUT | `/users/{user_id}/role` | Change user role (admin) |
| GET | `/tasks` | List, filter and search tasks |
| POST | `/tasks` | Create task |
| GET | `/tasks/{task_id}` | Task details |
| PUT | `/tasks/{task_id}` | Edit task |
| DELETE | `/tasks/{task_id}` | Delete task when permitted |
| PUT | `/tasks/{task_id}/assign` | Assign task (manager/admin) |
| GET | `/tasks/{task_id}/history` | History for an accessible task |
| GET | `/audit-logs` | Global audit logs (manager/admin) |
| GET | `/notifications` | Personal notifications |
| PUT | `/notifications/{notification_id}/read` | Mark notification as read |

`GET /tasks` supports query parameters `status`, `priority` and `search`. Services also provide `/health` and Swagger/OpenAPI endpoints.

## Repository structure

```text
microservices-backend-project/
├── auth-service/
├── task-service/
├── notification-service/
├── frontend/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

See [docs/](docs/) for additional architecture, communication, database and testing documentation.

## Testing and limitations

Manual functional, authorization, integration and infrastructure tests were documented in the thesis. These included authentication, task workflows, authorization responses (including HTTP 403), communication between services, local Docker execution, ECS/target-group health and CloudWatch logs.

This is an **academic MVP**, with the following known limitations:

- Some task fields need stronger client-side/server-side validation; incomplete values may be accepted.
- Deadline entry requires manual date/time input; improved controls and timezone handling are needed.
- Notifications are **in-app only** (no email, push or real-time delivery).
- No automated unit, integration or end-to-end test suite.
- No implemented CI/CD deployment pipeline.
- The AWS demo environment was not production-hardened (HTTPS, secrets management, auto-scaling and alarms are future improvements).

## Engineering thesis

This project was developed as the practical component of my 2026 engineering thesis at **Uniwersytet Dolnośląski IDEIS in Wrocław**, Computer Science — *Inżynier aplikacji i systemów chmurowych*.

**Thesis title:** *Projekt i implementacja chmurowej aplikacji backendowej typu Task Manager w architekturze mikroserwisów z wykorzystaniem AWS*.

**Author:** Alina Razumova

