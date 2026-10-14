// src/app/store.js
import { configureStore } from "@reduxjs/toolkit";
import authReducer, { clearAuth } from "../features/auth/authSlice";
import tasksReducer from "../features/tasks/tasksSlice";
import projectsReducer from "../features/projects/projectsSlice";
import projectMembersReducer from "../features/projectMembers/projectMembersSlice";
import { UNAUTHORIZED_EVENT } from "../api/axiosClient";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: tasksReducer,
    projects: projectsReducer,
    projectMembers: projectMembersReducer,
  },
});

// axiosClient không import store (tránh vòng lặp import) nên báo qua event
window.addEventListener(UNAUTHORIZED_EVENT, () => store.dispatch(clearAuth()));