export default function TaskHeader({ onNewTask, projectId }) {
  return (
    <header className="task-header">

      <h1>
        Tasks
        {projectId && <span className="task-header-project"> — Project #{projectId}</span>}
      </h1>

      <button
        type="button"
        className="new-task-button"
        onClick={onNewTask}
      >
        <span>+</span>
        New Task
      </button>

    </header>
  );
}