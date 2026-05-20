# Database Diagram

The project uses PostgreSQL as a relational database.

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string role
        datetime created_at
    }

    TASKS {
        int id PK
        string title
        text description
        string status
        string priority
        datetime deadline
        int owner_id
        int assigned_to
        datetime created_at
        datetime updated_at
    }

    NOTIFICATIONS {
        int id PK
        int user_id
        int task_id
        string title
        text message
        boolean is_read
        datetime created_at
    }

    USERS ||--o{ TASKS : owns
    USERS ||--o{ TASKS : assigned
    USERS ||--o{ NOTIFICATIONS : receives
    TASKS ||--o{ NOTIFICATIONS : generates
```

## Notes

The current implementation keeps service boundaries simple and stores identifiers such as `owner_id`, `assigned_to` and `user_id` as integer references. In a production system, this could be extended with stricter database-level foreign keys or separate databases per service.
