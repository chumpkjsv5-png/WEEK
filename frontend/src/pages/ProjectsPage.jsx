import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProjects } from "../hooks/useProjects";
import ProjectList from "../components/ProjectList";
import ProjectForm from "../components/ProjectForm";

export default function ProjectsPage() {
  const navigate = useNavigate();
  const { projects, status, error, addProject } = useProjects();
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  async function handleCreate(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      await addProject(payload);
      setShowForm(false);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleSelectProject(project) {
    navigate(`/tasks?project_id=${project.id}`);
  }

  return (
    <div className="page">

      <div className="page-header">
        <h1>Projects</h1>
        <button
          type="button"
          className="btn-primary"
          onClick={() => setShowForm((v) => !v)}
        >
          {showForm ? "Đóng" : "+ New Project"}
        </button>
      </div>

      {showForm && (
        <>
          <ProjectForm
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
            submitting={submitting}
          />
          {submitError && <div className="form-error">{submitError}</div>}
        </>
      )}

      <ProjectList
        status={status}
        projects={projects}
        error={error}
        onSelect={handleSelectProject}
      />

    </div>
  );
}