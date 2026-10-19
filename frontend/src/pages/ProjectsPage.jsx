import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import useDebounce from "../hooks/useDebounce";
import ProjectList from "../components/ProjectList";
import ProjectForm from "../components/ProjectForm";
import Search from "../components/Search";
import Pagination from "../components/Pagination";
import ProjectMembersPanel from "../components/ProjectMembersPanel";
import UserSelect from "../components/UserSelect";
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
import { selectUser, selectRole } from "../features/auth/authSelectors";

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

  // --- đăng nhập và quyền ---
  const user = useSelector(selectUser);
  const role = useSelector(selectRole);
  const isAdmin = role === "admin";
  const canCreate = ["admin", "manager"].includes(role);
  // admin sửa mọi project, manager chỉ sửa project mình sở hữu
  const canEditProject = (p) =>
    isAdmin || (role === "manager" && p.owner_id === user?.id);
  const canManageProject = (p) =>
  !!p && (isAdmin || (role === "manager" && p.owner_id === user?.id)); //admin and manager và là chủ project

  // --- state UI cục bộ ---
  const [showForm, setShowForm] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [actionError, setActionError] = useState("");
  const [editingProject, setEditingProject] = useState(null);
  const [membersProject, setMembersProject] = useState(null);

  const debouncedQuery = useDebounce(filters.search, 1000);
  const debouncedOwnerId = useDebounce(filters.ownerId, 500);

  const errMsg = (err) =>
    typeof err === "string" ? err : err?.message ?? "Có lỗi xảy ra";

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
        // Project mới: về trang 1 (đang ở trang 1 thì gọi tay)
        if (currentPage !== 1) dispatch(setPage(1));
        else load();
      }
      closeFormWithAnimation();
    } catch (err) {
      setSubmitError(errMsg(err));
    } finally {
      setSubmitting(false);
    }
  }

  function handleCancel() {
    closeFormWithAnimation();
  }

  function openCreateForm() {
    setEditingProject(null);
    setSubmitError("");
    setShowForm(true);
  }

  function openEditForm(project) {
    if (!canEditProject(project)) return; // backend vẫn chặn thật
    setEditingProject(project);
    setSubmitError("");
    setShowForm(true);
  }

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
      load();
    } catch (err) {
      setActionError(errMsg(err));
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
        {canCreate && (
          <Button icon="+" onClick={openCreateForm}>New Project</Button>
        )}
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
              isAdmin={isAdmin}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              submitting={submitting}
            />
            {submitError && <div className="form-error">{submitError}</div>}
          </div>
        </>
      )}

      {membersProject && (
        <>
          <div className="drawer-overlay" onClick={closeMembers} />
          <aside className="task-drawer">
            <div className="drawer-content">
              <ProjectMembersPanel
                project={membersProject}
                canManage={canManageProject(membersProject)}
                onClose={closeMembers}
              />
            </div>  
          </aside>
        </>
      )}

      <div className="project-search">
        <Search 
          value={filters.search}
          onChange={update("search")}
          placeholder="Search projects..."
        />
      </div>

      <div className="project-filters">
        <div className="filter-owner">
          <UserSelect
            value={filters.ownerId}
            onChange={update("ownerId")}
            placeholder="Lọc theo chủ sở hữu..."
          />
        </div>
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
        canEditProject={canManageProject}
        canDelete={canManageProject}
        onSelect={handleSelectProject}
        onEdit={openEditForm}
        onDelete={handleDelete}
        onMembers={openMembers}
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