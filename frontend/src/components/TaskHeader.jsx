// src/components/TaskHeader.jsx
import Button from "../components/Button";

export default function TaskHeader({ onNewTask, projectId }) {
  return (
    <header className="task-header">
      <h1>
        Tasks
        {projectId && <span className="task-header-project"> — Project #{projectId}</span>}
      </h1>

      <Button icon="+" onClick={onNewTask}>
        New Task
      </Button>
    </header>
  );
}
