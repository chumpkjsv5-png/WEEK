import axiosClient from "./axiosClient";

export async function login(email, password) {
  const res = await axiosClient.post("/auth/login", { email, password });
  return res.data; // { access_token, token_type }
}

export async function logout() {
  await axiosClient.post("/auth/logout");
}

export async function getMe(signal) {
  const res = await axiosClient.get("/auth/me", { signal });
  return res.data;
}