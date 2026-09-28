import { useState, useEffect } from "react";
import * as projectApi from "../api/projectApi";

export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      setStatus("loading");
      try {
        const data = await projectApi.getProjects();
        setProjects(data);
        setStatus("success");
      } catch (err) {
        setError(err.message);
        setStatus("error");
      }
    };

    fetchProjects();
  }, []);

  const addProject = async (payload) => {
    try {
      const newProject = await projectApi.createProject(payload);
      setProjects([newProject, ...projects]);
      return newProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateProjectItem = async (id, payload) => {
    try {
      const updatedProject = await projectApi.updateProject(id, payload);
      setProjects(
        projects.map((p) => (p.id === id ? updatedProject : p))
      );
      return updatedProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteProjectItem = async (id) => {
    try {
      await projectApi.deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
      return true;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return {
    projects,
    status,
    error,
    addProject,
    updateProjectItem,    // ← Thêm (tên khác để tránh conflict)
    deleteProjectItem,    // ← Thêm
  };
}