# Database diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string email
        string password_hash
        datetime created_at
    }

    ROLES {
        int id PK
        string name
    }

    USER_ROLES {
        int user_id FK
        int role_id FK
    }

    TASKS {
        int id PK
        string title
        string description
        string status
        string priority
        datetime deadline
        int assigned_user_id FK
        int created_by FK
        datetime created_at
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        int task_id FK
        string type
        string message
        boolean is_read
        datetime created_at
    }

    USERS ||--o{ TASKS : creates
    USERS ||--o{ TASKS : assigned_to
    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : contains
    USERS ||--o{ NOTIFICATIONS : receives
    TASKS ||--o{ NOTIFICATIONS : generates
