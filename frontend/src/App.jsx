import { useState } from "react";

import Sidebar from "./components/Sidebar";
import TaskHeader from "./components/TaskHeader";
import TaskTabs from "./components/TaskTabs";
import TaskSearch from "./components/TaskSearch";
import TaskForm from "./components/TaskForm";
import TaskList from "./components/TaskList";

import { useTasks } from "./hooks/useTasks";

import "./App.css";

export default function App() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [editingTask, setEditingTask] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");

  const {
    tasks,
    status,
    error,
    addTask,
    editTask,
    finishTask,
    removeTask,
  } = useTasks({
    search,
    statusFilter,
  });

  async function handleSubmit(payload) {
    setSubmitting(true);
    setActionError("");

    try {
      if (editingTask) {
        await editTask(editingTask.id, payload);
      } else {
        await addTask(payload);
      }

      setEditingTask(null);
      setShowForm(false);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleComplete(id) {
    setActionError("");

    try {
      await finishTask(id);
    } catch (err) {
      setActionError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Xoá task này?")) {
      return;
    }

    setActionError("");

    try {
      await removeTask(id);
    } catch (err) {
      setActionError(err.message);
    }
  }

  function openCreateForm() {
    setEditingTask(null);
    setActionError("");
    setShowForm(true);
  }

  function openEditForm(task) {
    setEditingTask(task);
    setActionError("");
    setShowForm(true);
  }

  function closeForm() {
    if (submitting) return;

    setShowForm(false);
    setEditingTask(null);
    setActionError("");
  }

  return (
    <div className="app">

      <Sidebar />

      <main className="main">

        <div className="page">

          <TaskHeader onNewTask={openCreateForm} />

          <TaskTabs
            value={statusFilter}
            onChange={setStatusFilter}
          />

          <TaskSearch
            value={search}
            onChange={setSearch}
          />

          {actionError && (
            <div className="action-error">
              {actionError}
            </div>
          )}

          <TaskList
            status={status}
            tasks={tasks}
            error={error}
            onEdit={openEditForm}
            onComplete={handleComplete}
            onDelete={handleDelete}
          />

        </div>

        {showForm && (
          <>

            <div
              className="drawer-overlay"
              onClick={closeForm}
            />

            <aside className="task-drawer">

              <div className="drawer-header">

                <h2>
                  {editingTask ? "Edit Task" : "New Task"}
                </h2>

                <button
                  className="drawer-close"
                  onClick={closeForm}
                  disabled={submitting}
                  type="button"
                >
                  ×
                </button>

              </div>

              <div className="drawer-content">

                <TaskForm
                  editingTask={editingTask}
                  onSubmit={handleSubmit}
                  onCancel={closeForm}
                  submitting={submitting}
                />

              </div>

            </aside>

          </>
        )}

      </main>

    </div>
  );
}