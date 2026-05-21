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

const allowedRoles = ['user', 'manager', 'admin'];
const deadlinePattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/;

function formatDeadlineForInput(value) {
  if (!value) return '';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return '';

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function normalizeDeadline(value) {
  if (!value) return null;

  if (!deadlinePattern.test(value)) {
    throw new Error('Invalid deadline format. Use: YYYY-MM-DD HH:mm');
  }

  return new Date(value.replace(' ', 'T')).toISOString();
}

function getUserName(users, userId) {
  if (!userId) return 'Not assigned';

  const user = users.find((item) => item.id === Number(userId));

  if (!user) return `User #${userId}`;

  return `${user.username} (${user.email})`;
}

function formatRole(role) {
  if (!role) return 'Unknown';
  return role.charAt(0).toUpperCase() + role.slice(1);
}

function statusLabel(status) {
  const labels = {
    todo: 'To do',
    in_progress: 'In progress',
    done: 'Done',
    cancelled: 'Cancelled',
  };

  return labels[status] || status;
}

function priorityLabel(priority) {
  const labels = {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
  };

  return labels[priority] || priority;
}

function roleDescription(role) {
  if (role === 'admin') {
    return 'Full access: users, roles, all tasks, assignments and audit logs.';
  }

  if (role === 'manager') {
    return 'Team access: all tasks, assignments and audit logs without role management.';
  }

  return 'Personal access: own and assigned tasks with personal notifications.';
}

function App() {
  const [authView, setAuthView] = useState(localStorage.getItem('token') ? 'dashboard' : 'welcome');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [me, setMe] = useState(null);
  const [users, setUsers] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [tasks, setTasks] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [message, setMessage] = useState('');
  const [taskForm, setTaskForm] = useState(emptyTaskForm);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editForm, setEditForm] = useState(emptyTaskForm);

  const authHeaders = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);
  const isAdmin = me?.role === 'admin';
  const isManager = me?.role === 'manager';
  const canAssignTasks = isAdmin || isManager;
  const canViewAuditLogs = isAdmin || isManager;
  const unreadNotifications = notifications.filter((notification) => !notification.is_read).length;

  async function request(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = data?.message || data?.detail?.message || data?.detail || response.statusText;
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

    setEmail('');
    setUsername('');
    setPassword('');

    setUsers([]);
    setUserSearch('');
    setTasks([]);
    setNotifications([]);
    setAuditLogs([]);

    setSearch('');
    setStatusFilter('');
    setPriorityFilter('');

    setTaskForm(emptyTaskForm);
    setEditingTaskId(null);
    setEditForm(emptyTaskForm);

    localStorage.removeItem('token');
    setAuthView('welcome');
    setMessage('');
  }

  async function loadMe() {
    if (!token) return;

    try {
      const data = await request(`${AUTH_API}/auth/me`, { headers: authHeaders });
      setMe(data);
    } catch (error) {
      setToken('');
      setMe(null);
      setUsers([]);
      setTasks([]);
      setNotifications([]);
      setAuditLogs([]);
      setTaskForm(emptyTaskForm);
      localStorage.removeItem('token');
      setAuthView('login');
      setMessage(`Session expired or invalid: ${error.message}`);
    }
  }

  async function loadUsers(searchValue = userSearch) {
    if (!token || !canAssignTasks) return;

    try {
      const params = new URLSearchParams();

      if (searchValue) params.set('search', searchValue);

      const data = await request(`${AUTH_API}/users?${params.toString()}`, {
        headers: authHeaders,
      });

      setUsers(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function changeUserRole(userId, role) {
    try {
      await request(`${AUTH_API}/users/${userId}/role`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify({ role }),
      });

      setMessage('User role updated successfully.');
      await loadUsers();
    } catch (error) {
      setMessage(error.message);
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
      const payload = {
        title: taskForm.title,
        description: taskForm.description,
        status: taskForm.status,
        priority: taskForm.priority,
        deadline: normalizeDeadline(taskForm.deadline.trim()),
        assigned_to: canAssignTasks && taskForm.assigned_to ? Number(taskForm.assigned_to) : null,
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
      if (canViewAuditLogs) {
        await loadAuditLogs();
      }
    } catch (error) {
      setMessage(error.message);
    }
  }

  function startEditTask(task) {
    setEditingTaskId(task.id);
    setEditForm({
      title: task.title || '',
      description: task.description || '',
      status: task.status || 'todo',
      priority: task.priority || 'medium',
      deadline: formatDeadlineForInput(task.deadline),
      assigned_to: task.assigned_to ? String(task.assigned_to) : '',
    });
  }

  function cancelEditTask() {
    setEditingTaskId(null);
    setEditForm(emptyTaskForm);
  }

  async function saveTaskChanges(taskId) {
    try {
      const payload = {
        title: editForm.title,
        description: editForm.description,
        status: editForm.status,
        priority: editForm.priority,
        deadline: normalizeDeadline(editForm.deadline.trim()),
      };

      if (canAssignTasks) {
        payload.assigned_to = editForm.assigned_to ? Number(editForm.assigned_to) : null;
      }

      await request(`${TASK_API}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders },
        body: JSON.stringify(payload),
      });

      setMessage('Task updated successfully.');
      cancelEditTask();

      await loadTasks();
      await loadNotifications();
      if (canViewAuditLogs) {
        await loadAuditLogs();
      }
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
      if (canViewAuditLogs) {
        await loadAuditLogs();
      }
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

  async function loadAuditLogs() {
    if (!token || !canViewAuditLogs) return;

    try {
      const data = await request(`${TASK_API}/audit-logs`, {
        headers: authHeaders,
      });

      setAuditLogs(data);
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

  useEffect(() => {
    if (token && me) {
      loadTasks();
      loadNotifications();
      if (canViewAuditLogs) {
        loadAuditLogs();
      } else {
        setAuditLogs([]);
      }
    }
  }, [token, me, canViewAuditLogs]);

  useEffect(() => {
    if (token && canAssignTasks) {
      loadUsers('');
    }
  }, [token, canAssignTasks]);

  if (!token || authView !== 'dashboard') {
    return (
      <main className="auth-page">
        <section className="auth-shell">
          <div className="auth-illustration">
            <p className="eyebrow">Microservices backend project</p>
            <h1>Cloud Task Manager</h1>
            <p>
              A role-based task system with authentication, task workflow, personal notifications and audit history.
            </p>
            <div className="feature-list">
              <span>JWT Auth</span>
              <span>RBAC</span>
              <span>Tasks</span>
              <span>Audit</span>
            </div>
          </div>

          {authView === 'welcome' && (
            <section className="auth-card compact-card">
              <p className="eyebrow">Welcome</p>
              <h2>Start working</h2>
              <p className="lead-small">
                Log in to manage your tasks. Create an account if this is the first run of the system.
              </p>
              <button onClick={() => { setAuthView('login'); setMessage(''); }}>Go to login</button>
              <button className="secondary" onClick={() => { setAuthView('register'); setMessage(''); }}>Create account</button>
            </section>
          )}

          {authView === 'loggedOut' && (
            <section className="auth-card compact-card">
              <p className="eyebrow">Logout</p>
              <h2>You are logged out</h2>
              <p className="lead-small">Your local JWT token has been removed.</p>
              <button onClick={() => { setAuthView('login'); setMessage(''); }}>Go to login</button>
              {message && <p className="message">{message}</p>}
            </section>
          )}

          {authView === 'login' && (
            <section className="auth-card compact-card">
              <p className="eyebrow">Login</p>
              <h2>Sign in</h2>
              <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Your email" />
              <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" type="password" />
              <button onClick={login}>Login</button>
              <div className="link-row">
                <button className="text-button" onClick={() => { setAuthView('register'); setMessage(''); }}>Create account</button>
                <button className="text-button" onClick={() => { setAuthView('welcome'); setMessage(''); }}>Back</button>
              </div>
              {message && <p className="message">{message}</p>}
            </section>
          )}

          {authView === 'register' && (
            <section className="auth-card compact-card">
              <p className="eyebrow">Register</p>
              <h2>Create account</h2>
              <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Your email" />
              <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Your username" />
              <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" type="password" />
              <button onClick={register}>Register</button>
              <p className="hint">The first registered user becomes admin automatically.</p>
              <div className="link-row">
                <button className="text-button" onClick={() => { setAuthView('login'); setMessage(''); }}>I already have an account</button>
                <button className="text-button" onClick={() => { setAuthView('welcome'); setMessage(''); }}>Back</button>
              </div>
              {message && <p className="message">{message}</p>}
            </section>
          )}
        </section>
      </main>
    );
  }

  return (
    <main className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">CT</div>
          <div>
            <strong>Cloud Tasks</strong>
            <span>Microservices MVP</span>
          </div>
        </div>

        <nav className="nav-list">
          <a href="#overview">Overview</a>
          <a href="#create">Create task</a>
          <a href="#tasks">Tasks</a>
          {isAdmin && <a href="#users">Users</a>}
          {canViewAuditLogs && <a href="#audit">Audit log</a>}
          <a href="#notifications">Notifications</a>
        </nav>

        <div className="sidebar-card">
          <span className={`role-badge role-${me?.role}`}>{formatRole(me?.role)}</span>
          <p>{roleDescription(me?.role)}</p>
        </div>

        <button className="logout" onClick={logout}>Logout</button>
      </aside>

      <section className="content">
        <section className="topbar" id="overview">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h1>Task workspace</h1>
            <p className="muted">Logged in as {me?.username} ({me?.email})</p>
          </div>
          <button onClick={() => { loadTasks(); loadNotifications(); if (canViewAuditLogs) loadAuditLogs(); }}>
            Refresh data
          </button>
        </section>

        {message && <p className="message global-message">{message}</p>}

        <section className="stats-grid">
          <article className="stat-card">
            <span>Tasks visible</span>
            <strong>{tasks.length}</strong>
            <p>{canAssignTasks ? 'Team workspace' : 'Own and assigned tasks'}</p>
          </article>
          <article className="stat-card">
            <span>Unread notifications</span>
            <strong>{unreadNotifications}</strong>
            <p>Personal notification feed</p>
          </article>
          <article className="stat-card">
            <span>Users loaded</span>
            <strong>{users.length}</strong>
            <p>{canAssignTasks ? 'Available for assignment' : 'Hidden for regular users'}</p>
          </article>
          <article className="stat-card">
            <span>Audit events</span>
            <strong>{canViewAuditLogs ? auditLogs.length : '—'}</strong>
            <p>{canViewAuditLogs ? 'Manager/Admin view' : 'Not available for user'}</p>
          </article>
        </section>

        {isAdmin && (
          <section className="panel" id="users">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Admin panel</p>
                <h2>Users and roles</h2>
                <p className="muted">Search users and change roles between user, manager and admin.</p>
              </div>
              <button onClick={() => loadUsers()}>Load users</button>
            </div>

            <div className="toolbar">
              <input value={userSearch} onChange={(event) => setUserSearch(event.target.value)} placeholder="Search users by email or username" />
              <button onClick={() => loadUsers()}>Search users</button>
            </div>

            <div className="list">
              {users.length === 0 && <p className="empty-state">No users loaded yet.</p>}
              {users.map((user) => (
                <article className="user-row" key={user.id}>
                  <div>
                    <h3>{user.username}</h3>
                    <p>ID: {user.id} · {user.email}</p>
                  </div>
                  <select value={user.role} onChange={(event) => changeUserRole(user.id, event.target.value)}>
                    {allowedRoles.map((role) => (
                      <option value={role} key={role}>{role}</option>
                    ))}
                  </select>
                </article>
              ))}
            </div>
          </section>
        )}

        <section className="panel" id="create">
          <div className="panel-header">
            <div>
              <p className="eyebrow">New task</p>
              <h2>Create task</h2>
              <p className="muted">
                Regular users create personal tasks. Managers and admins can assign tasks to team members.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <input value={taskForm.title} onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })} placeholder="Task title" />
            <input type="text" value={taskForm.deadline} onChange={(event) => setTaskForm({ ...taskForm, deadline: event.target.value })} placeholder="Deadline: YYYY-MM-DD HH:mm" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}" title="Use format: YYYY-MM-DD HH:mm, for example 2026-05-20 23:59" />
            <textarea className="span-2" value={taskForm.description} onChange={(event) => setTaskForm({ ...taskForm, description: event.target.value })} placeholder="Task description" />
            <select value={taskForm.status} onChange={(event) => setTaskForm({ ...taskForm, status: event.target.value })}>
              <option value="todo">To do</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select value={taskForm.priority} onChange={(event) => setTaskForm({ ...taskForm, priority: event.target.value })}>
              <option value="low">Low priority</option>
              <option value="medium">Medium priority</option>
              <option value="high">High priority</option>
            </select>

            {canAssignTasks ? (
              <select className="span-2" value={taskForm.assigned_to} onChange={(event) => setTaskForm({ ...taskForm, assigned_to: event.target.value })}>
                <option value="">Assign to: nobody</option>
                {users.map((user) => (
                  <option value={user.id} key={user.id}>{user.username} ({user.email})</option>
                ))}
              </select>
            ) : (
              <p className="hint span-2">Regular users create tasks only for themselves. Assignment is available for managers and admins.</p>
            )}

            <button className="span-2" onClick={createTask}>Create task</button>
          </div>
        </section>

        <section className="panel" id="tasks">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Work board</p>
              <h2>Tasks</h2>
              <p className="muted">Use filters, change status quickly, or open edit mode for full updates.</p>
            </div>
            <button onClick={loadTasks}>Load tasks</button>
          </div>

          <div className="toolbar">
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search title or description" />
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="">All statuses</option>
              <option value="todo">To do</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)}>
              <option value="">All priorities</option>
              <option value="low">Low priority</option>
              <option value="medium">Medium priority</option>
              <option value="high">High priority</option>
            </select>
          </div>

          <div className="task-list">
            {tasks.length === 0 && <p className="empty-state">No tasks found. Create one or click Load tasks.</p>}
            {tasks.map((task, index) => (
              <article className="task-card" key={task.id}>
                {editingTaskId === task.id ? (
                  <div className="edit-form">
                    <div className="panel-header compact">
                      <div>
                        <p className="eyebrow">Edit mode</p>
                        <h3>Edit task</h3>
                      </div>
                      <button className="secondary" onClick={cancelEditTask}>Cancel</button>
                    </div>

                    <input value={editForm.title} onChange={(event) => setEditForm({ ...editForm, title: event.target.value })} placeholder="Task title" />
                    <textarea value={editForm.description} onChange={(event) => setEditForm({ ...editForm, description: event.target.value })} placeholder="Task description" />
                    <div className="form-grid compact-grid">
                      <select value={editForm.status} onChange={(event) => setEditForm({ ...editForm, status: event.target.value })}>
                        <option value="todo">To do</option>
                        <option value="in_progress">In progress</option>
                        <option value="done">Done</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                      <select value={editForm.priority} onChange={(event) => setEditForm({ ...editForm, priority: event.target.value })}>
                        <option value="low">Low priority</option>
                        <option value="medium">Medium priority</option>
                        <option value="high">High priority</option>
                      </select>
                      <input type="text" value={editForm.deadline} onChange={(event) => setEditForm({ ...editForm, deadline: event.target.value })} placeholder="Deadline: YYYY-MM-DD HH:mm" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}" title="Use format: YYYY-MM-DD HH:mm, for example 2026-05-20 23:59" />
                      {canAssignTasks && (
                        <select value={editForm.assigned_to} onChange={(event) => setEditForm({ ...editForm, assigned_to: event.target.value })}>
                          <option value="">Assign to: nobody</option>
                          {users.map((user) => (
                            <option value={user.id} key={user.id}>{user.username} ({user.email})</option>
                          ))}
                        </select>
                      )}
                    </div>

                    <button onClick={() => saveTaskChanges(task.id)}>Save changes</button>
                  </div>
                ) : (
                  <>
                    <div className="task-card-header">
                      <div>
                        <span className="task-number">#{index + 1}</span>
                        <h3>{task.title}</h3>
                      </div>
                      <div className="badge-row">
                        <span className={`badge status-${task.status}`}>{statusLabel(task.status)}</span>
                        <span className={`badge priority-${task.priority}`}>{priorityLabel(task.priority)}</span>
                      </div>
                    </div>

                    <p className="task-description">{task.description}</p>

                    <div className="task-meta-grid">
                      <span><b>Owner:</b> {getUserName(users, task.owner_id)}</span>
                      <span><b>Assigned:</b> {getUserName(users, task.assigned_to)}</span>
                      <span><b>Deadline:</b> {task.deadline ? formatDeadlineForInput(task.deadline) : 'No deadline'}</span>
                    </div>

                    <div className="action-row">
                      <button onClick={() => startEditTask(task)}>Edit</button>
                      <button className="secondary" onClick={() => updateTaskStatus(task.id, 'in_progress')}>Start</button>
                      <button className="secondary" onClick={() => updateTaskStatus(task.id, 'done')}>Done</button>
                      {(isAdmin || task.owner_id === me?.id) && <button className="danger" onClick={() => deleteTask(task.id)}>Delete</button>}
                    </div>
                  </>
                )}
              </article>
            ))}
          </div>
        </section>

        {canViewAuditLogs && (
          <section className="panel" id="audit">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Control history</p>
                <h2>Audit log</h2>
                <p className="muted">Administrative history for task changes. Visible only to managers and admins.</p>
              </div>
              <button onClick={loadAuditLogs}>Load audit logs</button>
            </div>

            <div className="timeline">
              {auditLogs.length === 0 && <p className="empty-state">No audit events loaded yet.</p>}
              {auditLogs.map((log) => (
                <article className="timeline-item" key={log.id}>
                  <div className="timeline-dot" />
                  <div>
                    <h3>{log.action}</h3>
                    <p className="muted">Task ID: {log.task_id || '-'} · User ID: {log.actor_id} · {formatDeadlineForInput(log.created_at)}</p>
                    <p>{log.details || 'No details'}</p>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        <section className="panel" id="notifications">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Personal feed</p>
              <h2>Notifications</h2>
              <p className="muted">Only events addressed to the logged-in user are shown here.</p>
            </div>
            <button onClick={loadNotifications}>Load notifications</button>
          </div>

          <div className="notification-list">
            {notifications.length === 0 && <p className="empty-state">No notifications yet.</p>}
            {notifications.map((notification) => (
              <article className={`notification-card ${notification.is_read ? 'is-read' : ''}`} key={notification.id}>
                <div>
                  <h3>{notification.title}</h3>
                  <p>{notification.message}</p>
                  <span>{notification.is_read ? 'Read' : 'Unread'}</span>
                </div>

                {!notification.is_read && <button onClick={() => markNotificationRead(notification.id)}>Mark as read</button>}
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
