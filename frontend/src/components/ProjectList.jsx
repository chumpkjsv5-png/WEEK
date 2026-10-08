import RowActionsMenu from "./RowActionsMenu";
export default function ProjectList({
  status,
  projects,
  error,
  checkedProjects,
  onCheckProject,
  onSelect,
  onEdit,
  onDelete,
  onMembers, // MỚI
}

) {
  if (status === "loading") {
    return <div className="state-message">Đang tải danh sách project...</div>;
  }

  if (status === "error") {
    return (
      <div className="state-message state-error">
        Không tải được project: {error}
      </div>
    );
  }

  if (status === "success" && projects.length === 0) {
    return <div className="state-message">Chưa có project nào.</div>;
  }

  function formatDate(dateString) {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-CA");
  }

  return (
    <div className="project-table">
      <div className="project-table-header">
        <div className="name-col">NAME</div>
        <div className="date-col">CREATED AT</div>
        <div className="actions-col">ACTIONS</div>
      </div>

      {projects.map((project) => (
        <div className="project-table-row" key={project.id}>
          <div className="name-col">
            <div className="project-name">{project.name}</div>
            {project.description && (
              <div className="project-description" title={project.description}>
                {project.description}
              </div>
            )}
          </div>

          <div className="date-col">{formatDate(project.created_at)}</div>

          <div className="actions-col">
            <button
              type="button"
              className="action-btn view-btn"
              onClick={() => onSelect(project)}
              title="Xem task của project này"
            >
              Xem
            </button>

            <RowActionsMenu
              items={[
                { label: "Thành viên", onClick: () => onMembers(project) },
                { label: "Sửa", onClick: () => onEdit(project) },
                { label: "Xoá", danger: true, onClick: () => onDelete(project.id) },
              ]}
            />
          </div>
        </div>
      ))}
    </div>
  );
}