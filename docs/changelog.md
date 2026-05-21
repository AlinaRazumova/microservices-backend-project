# Changelog

## Final MVP version

### Added

- React frontend dashboard.
- Login, register and logout flow in the frontend.
- Task creation form.
- Task filtering and searching in the frontend.
- Task editing form in the frontend.
- Task assignment through a users dropdown instead of manually typing user ids.
- Administrator users panel in the frontend.
- User role management from the frontend.
- Notification Service.
- Notifications list in the frontend.
- Mark notification as read action.
- Deadline validation in frontend using `YYYY-MM-DD HH:mm` format.
- Testing guide for role-based authorization and task visibility.

### Improved

- README now describes the implemented final version instead of planned features only.
- Frontend no longer displays technical task ids as user-facing numbers.
- Task list uses simple visible numbering for presentation.
- Create task form clears after successful submission.
- Logout clears local JWT token and local form state.

### Security / Authorization

- JWT authentication protects task endpoints.
- Regular users see only owned or assigned tasks.
- Regular users cannot access the users list.
- Regular users cannot change roles.
- Task deletion is limited to task owner or administrator.
- Administrator can manage users and roles.

### Future work

- AWS deployment.
- CI/CD pipeline.
- Advanced audit log.
- Centralized monitoring/logging.
- Password reset flow.

## Role-based access update

- Added explicit manager role permissions.
- Managers can see all tasks and assign/edit tasks.
- Managers can load users for assignment but cannot change roles.
- Regular users no longer see the task assignment field in the frontend.
- Backend rejects task assignment attempts from regular users.


## Additional compliance update

- Added request logging middleware to all FastAPI services.
- Added consistent JSON error handlers to all services.
- Added AuditLog model, task history endpoint and global audit log endpoint.
- Added service-to-service REST token validation through Auth Service.
- Confirmed required `GET /tasks/{id}` and `PUT /tasks/{id}/assign` endpoints.
- Documented health checks, audit testing and service-to-service communication testing.


## RBAC and notification cleanup

- Notifications are now personal for every role.
- Admin and manager can use global audit logs; regular users cannot.
- Regular users see only their own/assigned tasks and personal notifications.
- Frontend hides audit log for regular users.
- Frontend package versions were pinned to stable Vite 5 and React 18 for reliable Docker builds.
