import axiosClient from "./axiosClient";

/**
 * params: { search?, owner_id?, created_after?, created_before?, skip?, limit? }
 * created_after / created_before dạng "YYYY-MM-DD"
 */
export async function getProjects(params = {}, signal) {
  // Bỏ các giá trị rỗng để không gửi ?search=&owner_id= lên server
  const cleaned = Object.fromEntries(
    Object.entries(params).filter(
      ([, v]) => v !== undefined && v !== null && v !== ""
    )
  );
  const res = await axiosClient.get("/projects", { params: cleaned, signal });
  return res.data; // { items, total, skip, limit, has_more }
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
  // payload: { name?, description?, owner_id? } - cần ít nhất 1 trường
  const res = await axiosClient.put(`/projects/${id}`, payload);
  return res.data;
}

export async function deleteProject(id) {
  await axiosClient.delete(`/projects/${id}`);
  return true;
}