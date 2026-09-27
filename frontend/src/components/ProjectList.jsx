export default function ProjectList({ status, projects, error, onSelect }) {
  if (status === "loading") {
    return (
      <div className="state-message">
        Đang tải danh sách project...
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="state-message state-error">
        Không tải được project: {error}
      </div>
    );
  }

  if (status === "success" && projects.length === 0) {
    return (
      <div className="state-message">
        Chưa có project nào.
      </div>
    );
  }

  return (
    <div className="task-table">

      <div className="task-table-header">
        <div>Name</div>
        <div>Description</div>
        <div>Actions</div>
      </div>

      {projects.map((project) => (
        <div className="task-table-row" key={project.id}>

          <div className="task-information">
            <span className="task-title">{project.name}</span>
          </div>

          <div className="task-information">
            {project.description ? (
              <span className="task-description">{project.description}</span>
            ) : (
              <span className="task-description">—</span>
            )}
          </div>

          <div className="task-actions">
            <button
              type="button"
              className="action-button edit"
              onClick={() => onSelect(project)}
              title="Xem task của project này"
            >
              Xem task
            </button>
          </div>

        </div>
      ))}

    </div>
  );
}