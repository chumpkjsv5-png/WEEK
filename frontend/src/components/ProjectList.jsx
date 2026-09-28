export default function ProjectList({
  status,
  projects,
  error,
  checkedProjects,
  onCheckProject,
  onSelect,
  onEdit,
  onDelete,
}) {
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
        <div className="checkbox-col">
          <input type="checkbox" />
        </div>
        <div className="name-col">NAME</div>
        <div className="description-col">DESCRIPTION</div>
        <div className="date-col">CREATED AT</div>
        <div className="actions-col">ACTIONS</div>
      </div>

      {projects.map((project) => (
        <div className="project-table-row" key={project.id}>
          <div className="checkbox-col">
            <input
              type="checkbox"
              checked={checkedProjects.has(project.id)}
              onChange={() => onCheckProject(project.id)}
            />
          </div>

          <div className="name-col">
            <div className="project-name">{project.name}</div>
          </div>

          <div className="description-col">
            {project.description ? (
              <div className="project-description">{project.description}</div>
            ) : (
              <div className="project-description">—</div>
            )}
          </div>

          <div className="date-col">{formatDate(project.created_at)}</div>

          <div className="actions-col">
            <button
              className="action-btn view-btn"
              onClick={() => onSelect(project)}
              title="Xem task của project này"
            >
              Xem
            </button>
            <button
              className="action-btn edit-btn"
              onClick={() => onEdit(project)}
              title="Sửa project"
            >
              Sửa
            </button>
            <button
              className="action-btn delete-btn"
              onClick={() => onDelete(project.id)}
              title="Xoá project"
            >
              Xoá
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}