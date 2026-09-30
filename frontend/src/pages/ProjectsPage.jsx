import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useProjects } from "../hooks/useProjects";
import useDebounce from "../hooks/useDebounce";
import ProjectList from "../components/ProjectList";
import ProjectForm from "../components/ProjectForm";
import TaskSearch from "../components/TaskSearch";
import Pagination from "../components/Pagination";
import "../css/projects.css";

export default function ProjectsPage() {
  const navigate = useNavigate();

  const [showForm, setShowForm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [editingProject, setEditingProject] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [createdAfter, setCreatedAfter] = useState("");
  const [createdBefore, setCreatedBefore] = useState("");
  const [checkedProjects, setCheckedProjects] = useState(new Set());

  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const debouncedQuery = useDebounce(searchQuery, 1000);
  const debouncedOwnerId = useDebounce(ownerId, 500);

  const {
    projects,
    total,
    status,
    error,
    addProject,
    updateProjectItem,
    deleteProjectItem,
  } = useProjects({
    search: debouncedQuery,
    ownerId: debouncedOwnerId,
    createdAfter,
    createdBefore,
    page: currentPage,
    pageSize,
  });

  const totalPages = Math.ceil(total / pageSize);
  const hasFilters = searchQuery || ownerId || createdAfter || createdBefore;

  // Đổi bộ lọc -> về trang 1
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedQuery, debouncedOwnerId, createdAfter, createdBefore]);

  // Xóa hết project của trang cuối -> lùi 1 trang
  useEffect(() => {
    if (status === "success" && projects.length === 0 && currentPage > 1) {
      setCurrentPage((p) => p - 1);
    }
  }, [status, projects.length, currentPage]);

  function closeFormWithAnimation() {
    setIsClosing(true);
    setTimeout(() => {
      setShowForm(false);
      setIsClosing(false);
      setEditingProject(null);
    }, 300);
  }

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError("");
    try {
      if (editingProject) {
        await updateProjectItem(editingProject.id, payload);
      } else {
        await addProject(payload);
      }
      closeFormWithAnimation();
    } catch (err) {
      setSubmitError(err.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancel() {
    closeFormWithAnimation();
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

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <button type="button" className="btn-primary" onClick={openCreateForm}>
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
        <TaskSearch
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search projects..."
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


      {status === "success" && total === 0 && hasFilters && (
        <p className="empty-state">Không tìm thấy project phù hợp.</p>
      )}

      <ProjectList
        status={status}
        projects={projects}
        error={error}
        checkedProjects={checkedProjects}
        onCheckProject={handleCheckProject}
        onSelect={handleSelectProject}
        onEdit={openEditForm}
        onDelete={handleDelete}
      />

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          totalItems={total}
          itemsPerPage={pageSize}
        />
      )}
    </div>
  );
}