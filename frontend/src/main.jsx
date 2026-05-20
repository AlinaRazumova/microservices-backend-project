import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const AUTH_API = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001';
const TASK_API = import.meta.env.VITE_TASK_API_URL || 'http://localhost:8002';
const NOTIFICATION_API = import.meta.env.VITE_NOTIFICATION_API_URL || 'http://localhost:8003';

const emptyTaskForm = {
  title: '',
  description: '',
  status: 'todo',
  priority: 'medium',
  deadline: '',
  assigned_to: '',
};

function App() {
  const [authView, setAuthView] = useState(localStorage.getItem('token') ? 'dashboard' : 'welcome');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [me, setMe] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState('');
  const [taskForm, setTaskForm] = useState(emptyTaskForm);

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  async function request(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = data?.detail?.message || data?.detail || response.statusText;
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }

    return data;
  }

  async function register() {
    try {
      const data = await request(`${AUTH_API}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password }),
      });

      setMessage(`Account created for ${data.email}. Role: ${data.role}. You can log in now.`);
      setAuthView('login');
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function login() {
    try {
      const data = await request(`${AUTH_API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      setAuthView('dashboard');
      setMessage('Logged in successfully.');
    } catch (error) {
      setMessage(error.message);
    }
  }

  function logout() {
    setToken('');
    setMe(null);
    setTasks([]);
    setNotifications([]);
    setTaskForm(emptyTaskForm);
    localStorage.removeItem('token');
    setAuthView('loggedOut');
    setMessage('You have been logged out.');
  }

  async function loadMe() {
    if (!token) return;

    try {
      const data = await request(`${AUTH_API}/auth/me`, { headers: authHeaders });
      setMe(data);
    } catch (error) {
      setToken('');
      setMe(null);
      setTasks([]);
      setNotifications([]);
      setTaskForm(emptyTaskForm);
      localStorage.removeItem('token');
      setAuthView('login');
      setMessage(`Session expired or invalid: ${error.message}`);
    }
  }

  async function loadTasks() {
    if (!token) return;

    try {
      const params = new URLSearchParams();

      if (statusFilter) params.set('status', statusFilter);
      if (priorityFilter) params.set('priority', priorityFilter);
      if (search) params.set('search', search);

      const data = await request(`${TASK_API}/tasks?${params.toString()}`, {
        headers: authHeaders,
      });

      setTasks(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function createTask() {
    try {
      const deadlinePattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/;

      if (taskForm.deadline && !deadlinePattern.test(taskForm.deadline)) {
        setMessage('Invalid deadline format. Use: YYYY-MM-DD HH:mm');
        return;
      }

      const normalizedDeadline = taskForm.deadline.trim().replace(' ', 'T');

      const payload = {
        ...taskForm,
        deadline: normalizedDeadline ? new Date(normalizedDeadline).toISOString() : null,
        assigned_to: taskForm.assigned_to ? Number(taskForm.assigned_to) : null,
      };

      await request(`${TASK_API}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify(payload),
      });

      setMessage('Task created successfully.');
      setTaskForm(emptyTaskForm);

      await loadTasks();
      await loadNotifications();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function updateTaskStatus(taskId, status) {
    try {
      await request(`${TASK_API}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({ status }),
      });

      setMessage('Task status updated.');

      await loadTasks();
      await loadNotifications();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function deleteTask(taskId) {
    try {
      await request(`${TASK_API}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: authHeaders,
      });

      setMessage('Task deleted.');

      await loadTasks();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadNotifications() {
    if (!token) return;

    try {
      const data = await request(`${NOTIFICATION_API}/notifications`, {
        headers: authHeaders,
      });

      setNotifications(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function markNotificationRead(id) {
    try {
      await request(`${NOTIFICATION_API}/notifications/${id}/read`, {
        method: 'PUT',
        headers: authHeaders,
      });

      await loadNotifications();
    } catch (error) {
      setMessage(error.message);
    }
  }

  useEffect(() => {
    if (token) {
      loadMe();
    }
  }, [token]);

  if (!token || authView !== 'dashboard') {
    return (
      <main className="auth-page">
        {authView === 'welcome' && (
          <section className="auth-card welcome-card">
            <p className="eyebrow">Microservices backend project</p>
            <h1>Cloud Task Manager</h1>
            <p className="lead">
              A task management system with FastAPI microservices, JWT authorization,
              PostgreSQL, Docker and a simple React client.
            </p>

            <div className="auth-actions">
              <button
                onClick={() => {
                  setAuthView('login');
                  setMessage('');
                }}
              >
                Go to login
              </button>

              <button
                className="secondary"
                onClick={() => {
                  setAuthView('register');
                  setMessage('');
                }}
              >
                Create account
              </button>
            </div>
          </section>
        )}

        {authView === 'loggedOut' && (
          <section className="auth-card compact-card">
            <p className="eyebrow">Logout</p>
            <h1>You are logged out</h1>
            <p className="lead">
              Your local JWT token has been removed. Log in again to access the dashboard.
            </p>

            <button
              onClick={() => {
                setAuthView('login');
                setMessage('');
              }}
            >
              Go to login
            </button>

            {message && <p className="message">{message}</p>}
          </section>
        )}

        {authView === 'login' && (
          <section className="auth-card compact-card">
            <p className="eyebrow">Login</p>
            <h1>Sign in</h1>

            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Your email"
            />

            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              type="password"
            />

            <button onClick={login}>Login</button>

            <div className="link-row">
              <button
                className="text-button"
                onClick={() => {
                  setAuthView('register');
                  setMessage('');
                }}
              >
                Create account
              </button>

              <button
                className="text-button"
                onClick={() => {
                  setAuthView('welcome');
                  setMessage('');
                }}
              >
                Back
              </button>
            </div>

            {message && <p className="message">{message}</p>}
          </section>
        )}

        {authView === 'register' && (
          <section className="auth-card compact-card">
            <p className="eyebrow">Register</p>
            <h1>Create account</h1>

            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Your email"
            />

            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your username"
            />

            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              type="password"
            />

            <button onClick={register}>Register</button>

            <p className="hint">The first registered user becomes admin automatically.</p>

            <div className="link-row">
              <button
                className="text-button"
                onClick={() => {
                  setAuthView('login');
                  setMessage('');
                }}
              >
                I already have an account
              </button>

              <button
                className="text-button"
                onClick={() => {
                  setAuthView('welcome');
                  setMessage('');
                }}
              >
                Back
              </button>
            </div>

            {message && <p className="message">{message}</p>}
          </section>
        )}
      </main>
    );
  }

  return (
    <main className="page">
      <section className="hero dashboard-hero">
        <div>
          <p className="eyebrow">Microservices backend project</p>
          <h1>Cloud Task Manager</h1>
          <p>
            FastAPI microservices with JWT, PostgreSQL, Docker, Swagger and a simple React client.
          </p>

          {me && (
            <p className="pill">
              Logged in as {me.username} ({me.role})
            </p>
          )}
        </div>

        <button className="logout" onClick={logout}>
          Logout
        </button>
      </section>

      {message && <p className="message global-message">{message}</p>}

      <section className="grid single">
        <div className="card">
          <h2>Create task</h2>

          <input
            value={taskForm.title}
            onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
            placeholder="Your task title"
          />

          <textarea
            value={taskForm.description}
            onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
            placeholder="Your task description"
          />

          <select
            value={taskForm.status}
            onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
          >
            <option value="todo">To do</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>

          <select
            value={taskForm.priority}
            onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
          >
            <option value="low">Low priority</option>
            <option value="medium">Medium priority</option>
            <option value="high">High priority</option>
          </select>

          <input
            type="text"
            value={taskForm.deadline}
            onChange={(e) => setTaskForm({ ...taskForm, deadline: e.target.value })}
            placeholder="Deadline: YYYY-MM-DD HH:mm"
            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}"
            title="Use format: YYYY-MM-DD HH:mm, for example 2026-05-20 23:59"
          />

          <input
            value={taskForm.assigned_to}
            onChange={(e) => setTaskForm({ ...taskForm, assigned_to: e.target.value })}
            placeholder="Assigned user ID optional"
          />

          <button onClick={createTask}>Create task</button>
        </div>
      </section>

      <section className="card wide">
        <h2>Tasks</h2>

        <div className="filters">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search title or description"
          />

          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All statuses</option>
            <option value="todo">To do</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>

          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="">All priorities</option>
            <option value="low">Low priority</option>
            <option value="medium">Medium priority</option>
            <option value="high">High priority</option>
          </select>

          <button onClick={loadTasks}>Load tasks</button>
        </div>

        <div className="list">
          {tasks.map((task, index) => (
            <article className="item" key={task.id}>
              <h3>
                {index + 1}. {task.title}
              </h3>

              <p>{task.description}</p>

              <p>
                Status: <b>{task.status}</b> | Priority: <b>{task.priority}</b> | Owner:{' '}
                {task.owner_id} | Assigned: {task.assigned_to || '-'}
              </p>

              <div className="row">
                <button onClick={() => updateTaskStatus(task.id, 'in_progress')}>Start</button>
                <button onClick={() => updateTaskStatus(task.id, 'done')}>Done</button>
                <button className="danger" onClick={() => deleteTask(task.id)}>
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="card wide">
        <h2>Notifications</h2>

        <button onClick={loadNotifications}>Load notifications</button>

        <div className="list">
          {notifications.map((notification) => (
            <article className="item" key={notification.id}>
              <h3>{notification.title}</h3>
              <p>{notification.message}</p>
              <p>{notification.is_read ? 'Read' : 'Unread'}</p>

              {!notification.is_read && (
                <button onClick={() => markNotificationRead(notification.id)}>Mark as read</button>
              )}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
