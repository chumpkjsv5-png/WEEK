import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useProjects } from "../hooks/useProjects";
import ProjectList from "../components/ProjectList";
import ProjectForm from "../components/ProjectForm";
import "../css/projects.css";

export default function ProjectsPage() {
  const navigate = useNavigate();
  const { projects, status, error, addProject, updateProjectItem, deleteProjectItem } = useProjects();
  const [showForm, setShowForm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [editingProject, setEditingProject] = useState(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [createdAfter, setCreatedAfter] = useState("");
  const [createdBefore, setCreatedBefore] = useState("");
  const [checkedProjects, setCheckedProjects] = useState(new Set());

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      if (editingProject) {
        await updateProjectItem(editingProject.id, payload);
      } else {
        await addProject(payload);
      }
      setIsClosing(true);
      setTimeout(() => {
        setShowForm(false);
        setIsClosing(false);
        setEditingProject(null);
      }, 300);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancel() {
    setIsClosing(true);
    setTimeout(() => {
      setShowForm(false);
      setIsClosing(false);
      setEditingProject(null);
    }, 300);
  }

  function handleCheckProject(projectId) {
    const newChecked = new Set(checkedProjects);
    if (newChecked.has(projectId)) {
      newChecked.delete(projectId);
    } else {
      newChecked.add(projectId);
    }
    setCheckedProjects(newChecked);
  }

  function openCreateForm() {
    setEditingProject(null);
    setSubmitError("");
    setShowForm(true);
  }

  function openEditForm(project) {
    setEditingProject(project);
    setSubmitError("");
    setShowForm(true);
  }

  async function handleDelete(projectId) {
    if (!window.confirm("Xoá project này?")) return;
    try {
      await deleteProjectItem(projectId);
    } catch (err) {
      setSubmitError(err.message);
    }
  }

  function handleSelectProject(project) {
    navigate(`/tasks?project_id=${project.id}`);
  }

  const filteredProjects = projects.filter((project) => {
    if (
      searchQuery &&
      !project.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
      return false;
    if (ownerId && project.owner_id !== ownerId) return false;
    if (createdAfter && new Date(project.created_at) < new Date(createdAfter))
      return false;
    if (
      createdBefore &&
      new Date(project.created_at) > new Date(createdBefore)
    )
      return false;
    return true;
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <button
          type="button"
          className="btn-primary"
          onClick={openCreateForm}
        >
          + New Project
        </button>
      </div>

      {showForm && (
        <>
          <div className="project-form-overlay" onClick={handleCancel} />
          <div
            className={`project-form-container ${
              isClosing ? "project-form-container-exit" : ""
            }`}
          >
            <h2>{editingProject ? "Sửa Project" : "Tạo Project Mới"}</h2>
            <ProjectForm
              editingProject={editingProject}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              submitting={submitting}
            />
            {submitError && <div className="form-error">{submitError}</div>}
          </div>
        </>
      )}

      <div className="project-search">
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="project-filters">
        <input
          type="text"
          placeholder="Owner ID"
          value={ownerId}
          onChange={(e) => setOwnerId(e.target.value)}
          className="filter-input"
        />
        <input
          type="date"
          value={createdAfter}
          onChange={(e) => setCreatedAfter(e.target.value)}
          className="filter-input"
        />
        <input
          type="date"
          value={createdBefore}
          onChange={(e) => setCreatedBefore(e.target.value)}
          className="filter-input"
        />
      </div>

      <ProjectList
        status={status}
        projects={filteredProjects}
        error={error}
        checkedProjects={checkedProjects}
        onCheckProject={handleCheckProject}
        onSelect={handleSelectProject}
        onEdit={openEditForm}
        onDelete={handleDelete}
      />
    </div>
  );
}