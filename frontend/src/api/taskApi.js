import axiosClient from "./axiosClient";

export async function getTasks({ search, status, skip = 0, limit = 100 } = {}) {
  const params = { skip, limit };
  if (search) params.search = search;
  if (status) params.status = status;

  const res = await axiosClient.get("/tasks/", { params });
  return res.data;
}

export async function createTask(payload) {
  const res = await axiosClient.post("/tasks/", payload);
  return res.data;
}

export async function updateTask(id, payload) {
  const res = await axiosClient.put(`/tasks/${id}`, payload);
  return res.data;
}

export async function completeTask(id) {
  const res = await axiosClient.patch(`/tasks/${id}/complete`);
  return res.data;
}

export async function deleteTask(id) {
  const res = await axiosClient.delete(`/tasks/${id}`);
  return res.data;
}