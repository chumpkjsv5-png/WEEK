// src/api/userApi.js
import axiosClient from "./axiosClient";

export async function getUsers() {
  const res = await axiosClient.get("/users/");
  return res.data;
}