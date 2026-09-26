import { useState, useEffect, useCallback } from "react";
import { getTasks, createTask, updateTask, completeTask, deleteTask } from "../api/taskApi";

export function useTasks({ search, statusFilter }) {
  const [tasks, setTasks] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [error, setError] = useState("");

  const loadTasks = useCallback(async () => {
    setStatus("loading");
    setError("");
    try {
      const data = await getTasks({ search, status: statusFilter || undefined });
      setTasks(data);
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const timer = setTimeout(loadTasks, 300); // debounce khi gõ search
    return () => clearTimeout(timer);
  }, [loadTasks]);

  async function addTask(payload) {
    await createTask(payload);
    await loadTasks();
  }

  async function editTask(id, payload) {
    await updateTask(id, payload);
    await loadTasks();
  }

  async function finishTask(id) {
    await completeTask(id);
    await loadTasks();
  }

  async function removeTask(id) {
    await deleteTask(id);
    await loadTasks();
  }

  return { tasks, status, error, addTask, editTask, finishTask, removeTask };
}