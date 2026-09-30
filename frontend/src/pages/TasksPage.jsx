import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import { TASK_PRIORITY_OPTIONS } from "../constants/taskPriority";
import TaskHeader from "../components/TaskHeader";
import TaskTabs from "../components/TaskTabs";
import TaskSearch from "../components/TaskSearch";
import TaskFilters from "../components/TaskFilters";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
import Pagination from "../components/Pagination";
import useDebounce from "../hooks/useDebounce";


import "../css/Main.css";

import { useTasks } from "../hooks/useTasks";

export default function TasksPage() {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("project_id");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [dueBefore, setDueBefore] = useState("");
  const [dueAfter, setDueAfter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const [editingTask, setEditingTask] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");

  const [priorityFilter, setPriorityFilter] = useState("");

  const debouncedSearch = useDebounce(search, 1000);

  useEffect(() => {
  setCurrentPage(1);
}, [debouncedSearch]);

  const {
    tasks,
    status,
    error,
    addTask,
    editTask,
    finishTask,
    removeTask,
  } = useTasks({
    search: debouncedSearch,
    statusFilter,
    priorityFilter, 
    projectId,
    assigneeId,
    dueBefore,
    dueAfter, 
  });

  // Pagination logic
  const totalPages = Math.ceil(tasks.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTasks = tasks.slice(startIndex, endIndex);

  function handleClearFilters() {
    setPriorityFilter("");
    setAssigneeId("");
    setDueBefore("");
    setDueAfter("");
    setCurrentPage(1);
  }

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  }

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
      setCurrentPage(1);
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
    if (!window.confirm("Xoá task này?")) return;
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
    <div className="page">
      <TaskHeader onNewTask={openCreateForm} projectId={projectId} />

      <TaskTabs 
        value={statusFilter} 
        onChange={(status) => {
          setStatusFilter(status);
          setCurrentPage(1);
        }} 
      />

      <TaskSearch 
        value={search} 
        onChange={setSearch} />

      <TaskFilters
        assigneeId={assigneeId}
        onAssigneeIdChange={(value) => {
          setAssigneeId(value);
          setCurrentPage(1);
        }}
        dueBefore={dueBefore}
        onDueBeforeChange={(value) => {
          setDueBefore(value);
          setCurrentPage(1);
        }}
        dueAfter={dueAfter}
        onDueAfterChange={(value) => {
          setDueAfter(value);
          setCurrentPage(1);
        }}
        onClear={handleClearFilters}
      />
      <div className="priority-filter">
        <select
          value={priorityFilter}
          onChange={(e) => {
            setPriorityFilter(e.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="">All priorities</option>
          {TASK_PRIORITY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {actionError && <div className="action-error">{actionError}</div>}

      <TaskList
        status={status}
        tasks={paginatedTasks}
        error={error}
        onEdit={openEditForm}
        onComplete={handleComplete}
        onDelete={handleDelete}
      />

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          totalItems={tasks.length}
          itemsPerPage={itemsPerPage}
        />
      )}

      {showForm && (
        <>
          <div className="drawer-overlay" onClick={closeForm} />
          <aside className="task-drawer">
            <div className="drawer-header">
              <h2>{editingTask ? "Edit Task" : "New Task"}</h2>
              <button className="drawer-close" onClick={closeForm} disabled={submitting} type="button">×</button>
            </div>
            <div className="drawer-content">
              <TaskForm
                editingTask={editingTask}
                defaultProjectId={projectId}
                onSubmit={handleSubmit}
                onCancel={closeForm}
                submitting={submitting}
              />
            </div>
          </aside>
        </>
      )}
    </div>
  );
}