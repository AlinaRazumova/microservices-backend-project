# Communication diagram

```mermaid
flowchart LR
    Client[Web Client]
    Auth[Auth Service]
    Task[Task Service]
    DB[(PostgreSQL)]
    Notif[Notification Service<br/>opcjonalnie]

    Client -->|REST API /register, /login| Auth
    Client -->|REST API /tasks| Task
    Task -->|weryfikacja tokenu / uprawnień| Auth
    Auth --> DB
    Task --> DB
    Task -. opcjonalnie .-> Notif
    Notif -. opcjonalnie .-> DB
