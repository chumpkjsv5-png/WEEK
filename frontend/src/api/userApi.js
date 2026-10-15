import axiosClient from "./axiosClient";

export async function searchUsers({ search, limit = 10 } = {}, signal) {
  const params = { limit };
  if (search) params.search = search;
  const res = await axiosClient.get("/users", { params, signal });
  return res.data; // { items, total }
}

export async function getUser(id, signal) {
  const res = await axiosClient.get(`/users/${id}`, { signal });
  return res.data;
}