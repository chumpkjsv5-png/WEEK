import {
  TASK_STATUS,
  TASK_STATUS_LABEL,
} from "../constants/taskStatus";
import { TASK_PRIORITY_LABEL } from "../constants/taskPriority";

export default function TaskList({
  status,
  tasks,
  error,
  onEdit,
  onComplete,
  onDelete,
}) {
  if (status === "loading") {
    return <div className="state-message">Đang tải danh sách task...</div>;
  }

  if (status === "error") {
    return (
      <div className="state-message state-error">
        Không tải được task: {error}
      </div>
    );
  }

  if (status === "success" && tasks.length === 0) {
    return <div className="state-message">Chưa có task nào.</div>;
  }

  return (
    <div className="task-table">
      <div className="task-table-header">
        <div>Title</div>
        <div>Status</div>
        <div>Priority</div>
        <div>Due Date</div>
        <div>Actions</div>
      </div>

      {tasks.map((task) => (
        <div className="task-table-row" key={task.id}>
          <div className="task-information">
            <span className="task-title">{task.title}</span>

            {task.description && (
              <span className="task-description">{task.description}</span>
            )}
          </div>

          <div>
            <span className={`status-badge status-${task.status}`}>
              {TASK_STATUS_LABEL[task.status] || task.status}
            </span>
          </div>

          <div>
            <span className={`priority-badge priority-${task.priority}`}>
              {TASK_PRIORITY_LABEL[task.priority] || task.priority}
            </span>
          </div>

          <div className="task-due-date">{task.due_date || "—"}</div>

          <div className="task-actions">
            {task.status !== TASK_STATUS.COMPLETED && (
              <button
                type="button"
                className="action-button complete"
                onClick={() => onComplete(task.id)}
                title="Hoàn thành"
              >
                ✓
              </button>
            )}

            <button
              type="button"
              className="action-button edit"
              onClick={() => onEdit(task)}
              title="Sửa"
            >
              Sửa
            </button>

            <button
              type="button"
              className="action-button delete"
              onClick={() => onDelete(task.id)}
              title="Xoá"
            >
              Xoá
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}