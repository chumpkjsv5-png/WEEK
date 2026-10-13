import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import useDebounce from "../hooks/useDebounce";
import ProjectList from "../components/ProjectList";
import ProjectForm from "../components/ProjectForm";
import TaskSearch from "../components/TaskSearch";
import Pagination from "../components/Pagination";
import ProjectMembersPanel from "../components/ProjectMembersPanel";
import Button from "../components/Button";
import "../css/projects.css";

import {
  fetchProjects, addProject, editProject, removeProject,
  setFilter, setPage,
} from "../features/projects/projectsSlice";
import {
  ITEMS_PER_PAGE, selectProjects, selectTotal, selectStatus, selectError,
  selectFilters, selectCurrentPage, selectTotalPages,
} from "../features/projects/projectsSelectors";

export default function ProjectsPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  // --- state từ Redux (đọc) ---
  const projects = useSelector(selectProjects);
  const total = useSelector(selectTotal);
  const status = useSelector(selectStatus);
  const error = useSelector(selectError);
  const filters = useSelector(selectFilters);
  const currentPage = useSelector(selectCurrentPage);
  const totalPages = useSelector(selectTotalPages);

  // --- state UI cục bộ (chỉ trang này dùng) ---
  const [showForm, setShowForm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [actionError, setActionError] = useState("");
  const [editingProject, setEditingProject] = useState(null);
  const [checkedProjects, setCheckedProjects] = useState(new Set());
  const [membersProject, setMembersProject] = useState(null); // MỚI: project đang mở panel thành viên

  const debouncedQuery = useDebounce(filters.search, 1000);
  const debouncedOwnerId = useDebounce(filters.ownerId, 500);

  // Tải danh sách khi bộ lọc / trang đổi, hoặc sau thêm-sửa-xóa (refreshKey)
  const load = useCallback(
    () =>
      dispatch(
        fetchProjects({
          search: debouncedQuery,
          ownerId: debouncedOwnerId,
          createdAfter: filters.createdAfter,
          createdBefore: filters.createdBefore,
          page: currentPage,
          limit: ITEMS_PER_PAGE,
        })
      ),
    [
      dispatch, debouncedQuery, debouncedOwnerId,
      filters.createdAfter, filters.createdBefore, currentPage,
    ]
  );

  // Đổi lọc hoặc trang -> gọi lại. Huỷ request cũ để tránh kết quả về sai thứ tự.
  useEffect(() => {
    const promise = load();
    return () => promise.abort();
  }, [load]);

  const update = (key) => (value) => dispatch(setFilter({ key, value }));

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
        await dispatch(editProject({ id: editingProject.id, payload })).unwrap();
        load();
      } else {
        await dispatch(addProject(payload)).unwrap();
        // Project mới: về trang 1 (đổi trang sẽ tự gọi lại, đang ở trang 1 thì gọi tay)
        if (currentPage !== 1) dispatch(setPage(1));
        else load();
      }
      closeFormWithAnimation();
    } catch (err) {
      setSubmitError(typeof err === "string" ? err : err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancel() {
    closeFormWithAnimation();
  }

  function handleCheckProject(projectId) {
    const next = new Set(checkedProjects);
    if (next.has(projectId)) next.delete(projectId);
    else next.add(projectId);
    setCheckedProjects(next);
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

  // MỚI
  function openMembers(project) {
    setActionError("");
    setMembersProject(project);
  }

  function closeMembers() {
    setMembersProject(null);
  }

  async function handleDelete(projectId) {
    if (!window.confirm("Xoá project này?")) return;
    setActionError("");
    try {
      await dispatch(removeProject(projectId)).unwrap();
      if (membersProject?.id === projectId) setMembersProject(null);
      load(); // nếu xóa project cuối của trang, slice tự lùi về trang trước
    } catch (err) {
      setActionError(typeof err === "string" ? err : err.message);
    }
  }

  function handleSelectProject(project) {
    navigate(`/tasks?project_id=${project.id}`);
  }

  function handlePageChange(page) {
    dispatch(setPage(page));
    window.scrollTo(0, 0);
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Projects</h1>
        <Button icon="+" onClick={openCreateForm}>New Project</Button>
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

      {/* MỚI: drawer thành viên, dùng lại class của TasksPage để giữ nguyên giao diện */}
      {membersProject && (
        <>
          <div className="drawer-overlay" onClick={closeMembers} />
          <aside className="task-drawer">
            <div className="drawer-content">
              <ProjectMembersPanel project={membersProject} onClose={closeMembers} />
            </div>
          </aside>
        </>
      )}

      <div className="project-search">
        <TaskSearch
          value={filters.search}
          onChange={update("search")}
          placeholder="Search projects..."
        />
      </div>

      <div className="project-filters">
        <input
          type="text"
          placeholder="Owner ID"
          value={filters.ownerId}
          onChange={(e) => update("ownerId")(e.target.value)}
          className="filter-input"
        />
        <input
          type="date"
          value={filters.createdAfter}
          onChange={(e) => update("createdAfter")(e.target.value)}
          className="filter-input"
        />
        <input
          type="date"
          value={filters.createdBefore}
          onChange={(e) => update("createdBefore")(e.target.value)}
          className="filter-input"
        />
      </div>

      {actionError && <div className="action-error">{actionError}</div>}

      <ProjectList
        status={status}
        projects={projects}
        error={error}
        checkedProjects={checkedProjects}
        onCheckProject={handleCheckProject}
        onSelect={handleSelectProject}
        onEdit={openEditForm}
        onDelete={handleDelete}
        onMembers={openMembers}   // MỚI
      />

      {totalPages > 1 && (
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
      />
      )}
    </div>
  );
}