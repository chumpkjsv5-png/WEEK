import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import {
  TASK_STATUS,
  TASK_STATUS_OPTIONS,
} from "../constants/taskStatus";
import {
  TASK_PRIORITY,
  TASK_PRIORITY_OPTIONS,
} from "../constants/taskPriority";
import { getProjects } from "../api/projectApi";
import { fetchMembers } from "../features/projectMembers/projectMembersSlice";
import {
  selectMembers, selectMembersStatus, selectMembersError,
} from "../features/projectMembers/projectMembersSelectors";

export default function TaskForm({
  editingTask,
  defaultProjectId,   // truyền từ component cha nếu đang ở màn "task của 1 project cụ thể"
  onSubmit,
  onCancel,
  submitting,
}) {
  const dispatch = useDispatch();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState(TASK_STATUS.PENDING);
  const [priority, setPriority] = useState(TASK_PRIORITY.MEDIUM);
  const [dueDate, setDueDate] = useState("");
  const [projectId, setProjectId] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState("");

  // Thành viên của project đang chọn (đọc từ store)
  const pid = projectId ? Number(projectId) : null;
  const members = useSelector((s) => selectMembers(s, pid));
  const membersStatus = useSelector((s) => selectMembersStatus(s, pid));
  const membersError = useSelector((s) => selectMembersError(s, pid));

  // Load danh sách project cho dropdown
  useEffect(() => {
    getProjects({ page: 1, page_size: 100 })
      .then((data) => setProjects(Array.isArray(data.items) ? data.items : []))
      .catch(() => setProjects([]));
  }, []);

  // Load thành viên mỗi khi đổi project
  useEffect(() => {
    if (!pid) return;
    const promise = dispatch(fetchMembers(pid));
    return () => promise.abort();
  }, [dispatch, pid]);

  useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title || "");
      setDescription(editingTask.description || "");
      setStatus(editingTask.status || TASK_STATUS.PENDING);
      setPriority(editingTask.priority || TASK_PRIORITY.MEDIUM);
      setDueDate(editingTask.due_date || "");
      setProjectId(editingTask.project_id || "");
      setAssigneeId(editingTask.assignee_id || "");
    } else {
      setTitle("");
      setDescription("");
      setStatus(TASK_STATUS.PENDING);
      setPriority(TASK_PRIORITY.MEDIUM);
      setDueDate("");
      setProjectId(defaultProjectId || "");
      setAssigneeId("");
    }

    setError("");
  }, [editingTask, defaultProjectId]);

  // Đổi project thì bỏ người được giao, vì người đó có thể không thuộc project mới
  function handleProjectChange(e) {
    setProjectId(e.target.value);
    setAssigneeId("");
  }

  function handleSubmit(e) {
    e.preventDefault();

    if (!title.trim()) {
      setError("Tên task không được để trống");
      return;
    }

    if (!projectId) {
      setError("Vui lòng chọn Project");
      return;
    }

    setError("");

    onSubmit({
      project_id: Number(projectId),
      title: title.trim(),
      description: description.trim() || null,
      status,
      priority,
      assignee_id: assigneeId || null,
      due_date: dueDate || null,
    });
  }

  // Task cũ có thể đang giao cho người không còn là thành viên
  const assigneeMissing =
    assigneeId &&
    membersStatus === "success" &&
    !members.some((m) => m.user_id === assigneeId);

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <div className="form-field">
        <label>
          Project <span>*</span>
        </label>
        <select value={projectId} onChange={handleProjectChange}>
          <option value="">-- Chọn project --</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-field">
        <label>
          Title <span>*</span>
        </label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Design homepage"
          maxLength={200}
          autoFocus
        />
      </div>

      <div className="form-field">
        <label>Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Create the main homepage for the project..."
          rows={4}
        />
      </div>

      <div className="form-field">
        <label>
          Status <span>*</span>
        </label>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {TASK_STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-field">
        <label>
          Priority <span>*</span>
        </label>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          {TASK_PRIORITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-field">
        <label>Assignee</label>
        <select
          value={assigneeId}
          onChange={(e) => setAssigneeId(e.target.value)}
          disabled={!pid || membersStatus === "loading"}
        >
          <option value="">
            {!pid
              ? "-- Chọn project trước --"
              : membersStatus === "loading"
              ? "Đang tải thành viên..."
              : "-- Chưa giao --"}
          </option>

          {members.map((m) => (
            <option key={m.user_id} value={m.user_id}>
              {m.user.full_name}
            </option>
          ))}

          {assigneeMissing && (
            <option value={assigneeId}>
              Người đã giao (không còn là thành viên)
            </option>
          )}
        </select>

        {pid && membersStatus === "error" && (
          <div className="form-error">
            Không tải được thành viên: {membersError}
          </div>
        )}
        {pid && membersStatus === "success" && members.length === 0 && (
          <small>Project chưa có thành viên. Thêm ở trang Projects.</small>
        )}
      </div>

      <div className="form-field">
        <label>Due Date</label>
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="form-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancel
        </button>

        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : editingTask ? "Save Changes" : "Create Task"}
        </button>
      </div>
    </form>
  );
}