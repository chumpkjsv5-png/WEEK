import { useState, useEffect, useCallback } from "react";
import * as projectApi from "../api/projectApi";

export function useProjects({
  search,
  ownerId,
  createdAfter,
  createdBefore,
  page = 1,
  pageSize = 10,
} = {}) {
  const [projects, setProjects] = useState([]);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const loadProjects = useCallback(
    async (signal) => {
      setStatus("loading");
      setError(null);
      try {
        const owner = ownerId?.trim();
        const data = await projectApi.getProjects(
          {
            search: search || undefined,
            owner_id: owner && /^\d+$/.test(owner) ? owner : undefined,
            created_after: createdAfter || undefined,
            created_before: createdBefore || undefined,
            page,
            page_size: pageSize,
          },
          signal
        );
        setProjects(Array.isArray(data.items) ? data.items : []);
        setTotal(data.total ?? 0);
        setStatus("success");
      } catch (err) {
        if (
          err.name === "CanceledError" ||
          err.name === "AbortError" ||
          err.code === "ERR_CANCELED"
        ) {
          return;
        }
        setError(err.message);
        setStatus("error");
      }
    },
    [search, ownerId, createdAfter, createdBefore, page, pageSize]
  );

  useEffect(() => {
    const controller = new AbortController();
    loadProjects(controller.signal);
    return () => controller.abort();
  }, [loadProjects]);

  const addProject = async (payload) => {
    try {
      const newProject = await projectApi.createProject(payload);
      await loadProjects();
      return newProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateProjectItem = async (id, payload) => {
    try {
      const updatedProject = await projectApi.updateProject(id, payload);
      await loadProjects();
      return updatedProject;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteProjectItem = async (id) => {
    try {
      await projectApi.deleteProject(id);
      await loadProjects();
      return true;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return {
    projects,
    total,
    status,
    error,
    addProject,
    updateProjectItem,
    deleteProjectItem,
  };
}