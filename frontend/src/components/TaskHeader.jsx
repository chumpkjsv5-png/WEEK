export default function TaskHeader({ onNewTask }) {
  return (
    <header className="task-header">

      <h1>Tasks</h1>

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