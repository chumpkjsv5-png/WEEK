import { useState, useEffect } from "react";

export default function ProjectForm({ editingProject, onSubmit, onCancel, submitting }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (editingProject) {
      setName(editingProject.name || "");
      setDescription(editingProject.description || "");
      setOwnerId(editingProject.owner_id || "");
    } else {
      setName("");
      setDescription("");
      setOwnerId("");
    }
    setError("");
  }, [editingProject]);

  function handleSubmit(e) {
    e.preventDefault();

    if (!name.trim()) {
      setError("Tên project không được để trống");
      return;
    }

    setError("");

    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      owner_id: ownerId.trim() || null,
    });
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>

      <div className="form-field">
        <label>Name <span>*</span></label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Website Redesign"
          maxLength={150}
          autoFocus
        />
      </div>

      <div className="form-field">
        <label>Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Redesign công ty landing page..."
          rows={4}
        />
      </div>

      <div className="form-field">
        <label>Owner ID (tuỳ chọn)</label>
        <input
          value={ownerId}
          onChange={(e) => setOwnerId(e.target.value)}
          placeholder="UUID của user, để trống nếu chưa có"
        />
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="form-actions">
        <button type="button" className="btn-secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Saving..." : editingProject ? "Update Project" : "Create Project"}
        </button>
      </div>

    </form>
  );
}