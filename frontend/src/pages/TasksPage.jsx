import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

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

import {
  fetchTasks, addTask, editTask, finishTask, removeTask,
  setFilter, clearFilters, setPage,
} from "../features/tasks/tasksSlice";
import {
  ITEMS_PER_PAGE, selectFilters, selectStatus, selectError,
  selectCurrentPage, selectTotalPages, selectPaginatedTasks, selectAllTasks,
} from "../features/tasks/tasksSelectors";

export default function TasksPage() {
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("project_id");

  // --- state từ Redux ---
  const filters = useSelector(selectFilters);
  const status = useSelector(selectStatus);
  const error = useSelector(selectError);
  const currentPage = useSelector(selectCurrentPage);
  const totalPages = useSelector(selectTotalPages);
  const paginatedTasks = useSelector(selectPaginatedTasks);
  const allTasks = useSelector(selectAllTasks);

  // --- state UI cục bộ ---
  const [editingTask, setEditingTask] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");

  const debouncedSearch = useDebounce(filters.search, 1000);

  // Gọi API mỗi khi filter đổi
  useEffect(() => {
    dispatch(
      fetchTasks({
        search: debouncedSearch,
        statusFilter: filters.statusFilter,
        priorityFilter: filters.priorityFilter,
        assigneeId: filters.assigneeId,
        dueBefore: filters.dueBefore,
        dueAfter: filters.dueAfter,
        projectId,
      })
    );
  }, [
    dispatch, debouncedSearch, projectId,
    filters.statusFilter, filters.priorityFilter,
    filters.assigneeId, filters.dueBefore, filters.dueAfter,
  ]);

  const update = (key) => (value) => dispatch(setFilter({ key, value }));

  async function handleSubmit(payload) {
    setSubmitting(true);
    setActionError("");
    try {
      if (editingTask) {
        await dispatch(editTask({ id: editingTask.id, payload })).unwrap();
      } else {
        await dispatch(addTask(payload)).unwrap();
      }
      setEditingTask(null);
      setShowForm(false);
      dispatch(setPage(1));
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleComplete(id) {
    setActionError("");
    try {
      await dispatch(finishTask(id)).unwrap();
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Xoá task này?")) return;
    setActionError("");
    try {
      await dispatch(removeTask(id)).unwrap();
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    }
  }

  function handlePageChange(page) {
    dispatch(setPage(page));
    window.scrollTo(0, 0);
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

      <TaskTabs value={filters.statusFilter} onChange={update("statusFilter")} />

      <TaskSearch value={filters.search} onChange={update("search")} />

      <TaskFilters
        assigneeId={filters.assigneeId}
        onAssigneeIdChange={update("assigneeId")}
        dueBefore={filters.dueBefore}
        onDueBeforeChange={update("dueBefore")}
        dueAfter={filters.dueAfter}
        onDueAfterChange={update("dueAfter")}
        onClear={() => dispatch(clearFilters())}
      />

      <div className="priority-filter">
        <select
          value={filters.priorityFilter}
          onChange={(e) => update("priorityFilter")(e.target.value)}
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
          totalItems={allTasks.length}
          itemsPerPage={ITEMS_PER_PAGE}
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