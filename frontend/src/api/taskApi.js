  import axiosClient from "./axiosClient";
  import { ITEMS_PER_PAGE } from "../features/tasks/tasksSelectors";

export async function getTasks({
  projectId,
  search,
  status,
  priority,
  assigneeId,
  dueBefore,
  dueAfter,
  sortByPriority = false,   // thêm
  skip = 0,
  limit = ITEMS_PER_PAGE,
} = {}) {
  const params = { skip, limit };
  if (projectId) params.project_id = projectId;
  if (search) params.search = search;
  if (status) params.status = status;
  if (priority) params.priority = priority;
  if (assigneeId) params.assignee_id = assigneeId;
  if (dueBefore) params.due_before = dueBefore;
  if (dueAfter) params.due_after = dueAfter;
  if (sortByPriority) params.sort_by_priority = true;   // thêm

  const res = await axiosClient.get("/tasks/", { params });
  return res.data; // { items, total, skip, limit, has_more }
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