import axiosClient from "./axiosClient";

export async function getTasks({
  projectId,        // Story 1: group by project
  search,
  status,
  assigneeId,        // Story 2: filter theo assignee
  dueBefore,          // Story 2: filter theo date
  dueAfter,
  skip = 0,
  limit = 100,
} = {}) {
  const params = { skip, limit };
  if (projectId) params.project_id = projectId;
  if (search) params.search = search;
  if (status) params.status = status;
  if (assigneeId) params.assignee_id = assigneeId;
  if (dueBefore) params.due_before = dueBefore;
  if (dueAfter) params.due_after = dueAfter;

  const res = await axiosClient.get("/tasks/", { params });
  return res.data; // { items, total, skip, limit }
}

export async function getTask(id) {
  const res = await axiosClient.get(`/tasks/${id}`);
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