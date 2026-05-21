# Testing Guide

This document describes how to test the final version of the microservices task management project.

## 1. Start the project

From the project root run:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

Expected containers:

- `microservices_postgres`
- `auth_service`
- `task_service`
- `notification_service`
- `frontend_client`

Expected local URLs:

- Frontend: `http://localhost:3000`
- Auth Swagger: `http://localhost:8001/docs`
- Task Swagger: `http://localhost:8002/docs`
- Notification Swagger: `http://localhost:8003/docs`

## 2. Register administrator

Open frontend:

```text
http://localhost:3000
```

Register the first user.

Example:

```json
{
  "email": "admin@example.com",
  "username": "admin",
  "password": "admin123"
}
```

Expected result:

- first registered user receives role `admin`
- login is possible after registration
- dashboard is displayed after login

You can verify the role in Auth Swagger:

```text
GET /auth/me
```

Expected response contains:

```json
{
  "role": "admin"
}
```

## 3. Register regular user

Create a second account, for example:

```json
{
  "email": "user@example.com",
  "username": "user",
  "password": "user123"
}
```

Expected result:

- second registered user receives role `user`

## 4. Admin users panel

Login as administrator in the frontend.

Expected behavior:

- admin sees the `Users` panel
- admin can load users
- admin can search users by email or username
- admin can see user id, email, username and role
- admin can change user role with a dropdown

Test role change:

1. Open the users panel.
2. Change regular user role from `user` to `manager`.
3. Keep this account as `manager` for the next manager workflow test.

Expected result:

- role changes successfully
- frontend displays success message
- `GET /users` in Auth Swagger also shows updated role

## 5. Create task with assignment

Login as administrator or manager.

Create a task in the frontend.

Example data:

```text
Title: Prepare documentation
Description: Prepare final project documentation
Status: To do
Priority: High priority
Deadline: 2026-05-20 23:59
Assign to: user@example.com
```

Expected result:

- task is created successfully
- task appears in task list
- assigned user is displayed by username/email instead of manual technical id
- notification is generated

## 6. Validate deadline format

Try to create a task with invalid deadline:

```text
20.05.2026 23:59
```

Expected result:

- frontend rejects the value
- message is displayed: `Invalid deadline format. Use: YYYY-MM-DD HH:mm`

Correct format:

```text
2026-05-20 23:59
```

## 7. Edit task

In the frontend task list click `Edit`.

Change:

- title
- description
- status
- priority
- deadline
- assigned user

Click `Save changes`.

Expected result:

- task is updated successfully
- task list refreshes
- updated values are visible
- notification is generated when status changes

## 8. Filter and search tasks

Use the task filters in the frontend:

- filter by status
- filter by priority
- search by title or description

Expected result:

- only matching tasks are displayed

The same can be checked in Task Swagger:

```text
GET /tasks?status=todo
GET /tasks?priority=high
GET /tasks?search=documentation
```

## 9. Notifications

In the frontend click `Load notifications`.

Expected result:

- task creation and task assignment notifications are visible
- unread notification can be marked as read

Swagger endpoints:

```text
GET /notifications
PUT /notifications/{notification_id}/read
```

## 10. Manager workflow test

Login as a user with role `manager`.

Expected behavior:

- manager can see all tasks
- manager can load the user list for assignment
- manager can assign tasks with the users dropdown
- manager can edit task status, priority and deadline
- manager does not see the admin role-management panel
- manager cannot change user roles

Swagger verification:

```text
GET /tasks
GET /users
PUT /users/{user_id}/role
```

Expected result:

- `GET /tasks` works
- `GET /users` works for assignment support
- `PUT /users/{user_id}/role` returns `403 Forbidden`

## 11. Authorization test: regular user cannot see all tasks

Login as regular user.

Expected behavior:

- regular user sees only own tasks or tasks assigned to them
- regular user does not see unrelated tasks owned by other users
- regular user does not see the admin users panel
- regular user does not see task assignment dropdown

Swagger verification:

1. Login as regular user in Auth Swagger.
2. Copy token.
3. Authorize Task Swagger with that token.
4. Execute `GET /tasks`.

Expected result:

- response contains only tasks where regular user is owner or assignee

## 12. Authorization test: regular user cannot manage users or roles

Use regular user token in Auth Swagger.

Try:

```text
GET /users
PUT /users/{user_id}/role
```

Expected result:

```text
403 Forbidden
```

The regular user should also be unable to assign tasks to other users.

## 13. Authorization test: regular user cannot delete another user's task

Use regular user token in Task Swagger.

Try to delete a task owned by another user:

```text
DELETE /tasks/{task_id}
```

Expected result:

```text
403 Forbidden
```

## 14. Stop project

```bash
docker compose down
```

To remove database data:

```bash
docker compose down -v --remove-orphans
```


## Additional requirement checks

### Consistent error format

Example invalid task id or invalid role should return:

```json
{
  "code": "TASK_NOT_FOUND",
  "message": "Task not found",
  "details": null
}
```

Validation errors return:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": []
}
```

### Task details endpoint

Use Task Service Swagger:

```text
GET /tasks/{task_id}
```

Expected: owner, assigned user, admin or manager can view according to RBAC rules. Other regular users receive `FORBIDDEN`.

### Task assignment endpoint

Use Task Service Swagger:

```text
PUT /tasks/{task_id}/assign
```

Expected: admin and manager can assign tasks. Regular user receives `FORBIDDEN`.

### Audit log / history

After creating, editing, assigning or deleting a task, check:

```text
GET /audit-logs
GET /tasks/{task_id}/history
```

Expected: audit records contain `actor_id`, `task_id`, `action`, `details`, `created_at`.

### Monitoring / logging

Check health endpoints:

```text
GET http://localhost:8001/health
GET http://localhost:8002/health
GET http://localhost:8003/health
```

Expected: each service returns `status: healthy`. Docker logs should show request method, path, response status and processing time.

### Service-to-service REST communication

Task Service and Notification Service call Auth Service through:

```text
GET /internal/auth/validate
```

Task Service also calls Notification Service through:

```text
POST /internal/notifications
```

This confirms microservice-to-microservice communication through HTTP REST API.


## RBAC, notifications and audit testing

1. Register the first user. The first registered account becomes `admin`.
2. Register a second account as a regular `user`.
3. As admin, create a task and assign it to the regular user. The assigned user should receive a personal notification.
4. Log in as the regular user. The user should see only their own or assigned tasks, should not see the assignment dropdown, should not see the Users admin panel, and should not see the global audit log block.
5. Create a personal task as the regular user. Only that user should receive the notification. Admin can still see the task in the global task list, but does not receive the user's private notification.
6. Change a user's role to `manager`. The manager should see all tasks and the audit log, and can assign/edit tasks, but cannot change user roles.
7. Confirm that `GET /notifications` returns only notifications for the logged-in user.
8. Confirm that `GET /audit-logs` is allowed for `admin` and `manager`, and forbidden for `user`.
9. Confirm that `GET /tasks/{task_id}/history` is allowed only for users who can access that task, and for admin/manager.
