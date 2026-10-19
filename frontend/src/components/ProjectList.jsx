import RowActionsMenu from "./RowActionsMenu";
import Button from "./Button";

export default function ProjectList({
  status,
  projects = [],
  error,
  canEditProject, // (project) => boolean
  canDelete,
  onSelect,
  onEdit,
  onDelete,
  onMembers,
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
        <div className="name-col">NAME</div>
        <div className="date-col">CREATED AT</div>
        <div className="actions-col">ACTIONS</div>
      </div>

      {projects.map((project) => {
        // Mục nào không đủ quyền thì không đưa vào menu
        const items = [
          onMembers && { label: "Thành viên", onClick: () => onMembers(project) },
          onEdit &&
            canEditProject?.(project) && {
              label: "Sửa",
              onClick: () => onEdit(project),
            },
          onDelete &&
            canDelete?.(project) && {
              label: "Xoá",
              danger: true,
              onClick: () => onDelete(project.id),
            },
        ].filter(Boolean);

        return (
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
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onSelect(project)}
                title="Xem task của project này"
              >
                Xem
              </Button>

              {items.length > 0 && <RowActionsMenu items={items} />}
            </div>
          </div>
        );
      })}
    </div>
  );
}