import { useEffect, useState } from "react";
import { getUsers } from "../api/userApi";

export default function TaskFilters({
  assigneeId,
  onAssigneeIdChange,
  dueBefore,
  onDueBeforeChange,
  dueAfter,
  onDueAfterChange,
}) {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    getUsers()
      .then((data) => setUsers(Array.isArray(data) ? data : data.items ?? []))
      .catch(() => setUsers([]));
  }, []);

  return (
    <div className="task-filters">
      <div className="filter-field">
        <label>Assignee</label>
        <select
          value={assigneeId}
          onChange={(e) => onAssigneeIdChange(e.target.value)}
        >
          <option value="">All assignees</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.full_name}
            </option>
          ))}
        </select>
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
    </div>
  );
}