// src/app/store.js
import { configureStore } from "@reduxjs/toolkit";
import tasksReducer from "../features/tasks/tasksSlice";
import projectsReducer from "../features/projects/projectsSlice";
import projectMembersReducer from "../features/projectMembers/projectMembersSlice";

export const store = configureStore({
  reducer: {
    tasks: tasksReducer,
    projects: projectsReducer,
    projectMembers: projectMembersReducer,
  },
});