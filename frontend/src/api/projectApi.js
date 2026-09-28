import axiosClient from "./axiosClient";

export async function getProjects() {
  const res = await axiosClient.get("/projects");
  return res.data;
}

export async function getProject(id) {
  const res = await axiosClient.get(`/projects/${id}`);
  return res.data;
}

export async function createProject(payload) {
  // payload: { name, description?, owner_id? }
  const res = await axiosClient.post("/projects", payload);
  return res.data;
}

export async function updateProject(id, payload) {
  // payload: { name?, description?, owner_id? }
  const res = await axiosClient.put(`/projects/${id}`, payload);
  return res.data;
}

export async function deleteProject(id) {
  await axiosClient.delete(`/projects/${id}`);
  return true;
}