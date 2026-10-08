// src/api/userApi.js
import axiosClient from "./axiosClient";

export async function getUsers(params = {}, signal) {
  const res = await axiosClient.get("/users/", { params, signal });
  return res.data; // mảng, hoặc { items, total } tùy backend
}