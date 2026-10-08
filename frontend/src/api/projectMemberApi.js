// src/api/projectMemberApi.js
import axiosClient from "./axiosClient";

export async function getProjectMembers(projectId, signal) {
  const res = await axiosClient.get(`/projects/${projectId}/members`, { signal });
  return res.data; // [{ project_id, user_id, user: { id, email, full_name } }]
}

export async function addProjectMember(projectId, userId) {
  const res = await axiosClient.post(`/projects/${projectId}/members`, {
    user_id: userId,
  });
  return res.data;
}

export async function removeProjectMember(projectId, userId) {
  await axiosClient.delete(`/projects/${projectId}/members/${userId}`);
  return userId; // 204 không có body, trả userId để reducer/UI biết cần bỏ ai
}