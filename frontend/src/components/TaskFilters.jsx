export default function TaskFilters({
  assigneeId,
  onAssigneeIdChange,
  dueBefore,
  onDueBeforeChange,
  dueAfter,
  onDueAfterChange,
  onClear,
}) {
  const hasActiveFilter = assigneeId || dueBefore || dueAfter;

  return (
    <div className="task-filters">

      <div className="filter-field">
        <label>Assignee ID</label>
        <input
          value={assigneeId}
          onChange={(e) => onAssigneeIdChange(e.target.value)}
          placeholder="UUID của người được giao"
        />
      </div>

      <div className="filter-field">
        <label>Due sau ngày</label>
        <input
          type="date"
          value={dueAfter}
          onChange={(e) => onDueAfterChange(e.target.value)}
        />
      </div>

      <div className="filter-field">
        <label>Due trước ngày</label>
        <input
          type="date"
          value={dueBefore}
          onChange={(e) => onDueBeforeChange(e.target.value)}
        />
      </div>

      {hasActiveFilter && (
        <button type="button" className="btn-secondary" onClick={onClear}>
          Xoá filter
        </button>
      )}

    </div>
  );
}