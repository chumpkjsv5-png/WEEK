import { useState, useEffect, useCallback } from "react";
import { getProjects, createProject } from "../api/projectApi";

export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [error, setError] = useState("");

  const loadProjects = useCallback(async () => {
    setStatus("loading");
    setError("");
    try {
      const data = await getProjects();
      setProjects(data);
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  async function addProject(payload) {
    await createProject(payload);
    await loadProjects();
  }

  return { projects, status, error, addProject };
}