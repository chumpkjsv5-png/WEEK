import { useState, useEffect } from "react";
import UserSelect from "./UserSelect";

export default function ProjectForm({
  editingProject,
  isAdmin = false,
  onSubmit,
  onCancel,
  submitting,
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [error, setError] = useState("");

  // Chỉ admin đang sửa project mới được thấy và đổi owner
  const canEditOwner = isAdmin && !!editingProject;

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

    const payload = {
      name: name.trim(),
      description: description.trim() || null,
    };

    // Chỉ gửi owner_id khi admin sửa và giá trị thật sự thay đổi.
    // Gửi thừa thì manager sẽ bị 403 "Chỉ admin mới được đổi chủ sở hữu".
    if (canEditOwner && ownerId.trim() && ownerId.trim() !== editingProject.owner_id) {
      payload.owner_id = ownerId.trim();
    }

    onSubmit(payload);
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

      {canEditOwner && (
        <div className="form-field">
          <label>Owner</label>
          <UserSelect value={ownerId} onChange={setOwnerId} />
          <small>Chỉ admin được đổi chủ sở hữu.</small>
        </div>
      )}

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