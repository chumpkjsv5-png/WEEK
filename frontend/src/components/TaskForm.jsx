import { useState, useEffect } from "react";

import {
  TASK_STATUS,
  TASK_STATUS_OPTIONS,
} from "../constants/taskStatus";

export default function TaskForm({
  editingTask,
  onSubmit,
  onCancel,
  submitting,
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState(TASK_STATUS.PENDING);
  const [dueDate, setDueDate] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title || "");
      setDescription(editingTask.description || "");
      setStatus(
        editingTask.status || TASK_STATUS.PENDING
      );
      setDueDate(editingTask.due_date || "");
    } else {
      setTitle("");
      setDescription("");
      setStatus(TASK_STATUS.PENDING);
      setDueDate("");
    }

    setError("");
  }, [editingTask]);

  function handleSubmit(e) {
    e.preventDefault();

    if (!title.trim()) {
      setError("Tên task không được để trống");
      return;
    }

    setError("");

    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      status,
      due_date: dueDate || null,
    });
  }

  return (
    <form
      className="task-form"
      onSubmit={handleSubmit}
    >

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

        <label>
          Description
        </label>

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

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >

          {TASK_STATUS_OPTIONS.map((option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          ))}

        </select>

      </div>

      <div className="form-field">

        <label>
          Due Date
        </label>

        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />

      </div>

      {error && (
        <div className="form-error">
          {error}
        </div>
      )}

      <div className="form-actions">

        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancel
        </button>

        <button
          type="submit"
          className="btn-primary"
          disabled={submitting}
        >
          {submitting
            ? "Saving..."
            : editingTask
              ? "Save Changes"
              : "Create Task"}
        </button>

      </div>

    </form>
  );
}