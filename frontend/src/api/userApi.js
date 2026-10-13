// src/api/userApi.js
import axiosClient from "./axiosClient";

export async function getUsers(params = {}, signal) {
  const res = await axiosClient.get("/users/", { params, signal });
  return res.data; // mảng, hoặc { items, total } tùy backend
}

// export async function getUser(id, signal) {
//   const res = await axiosClient.get(`/users/${id}`, { signal });
//   return res.data;
// }

// export async function updateUserRole(id, role) {
//   const res = await axiosClient.patch(`/users/${id}`, { role });
//   return res.data;
// }