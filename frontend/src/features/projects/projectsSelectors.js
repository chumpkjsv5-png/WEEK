// src/features/projects/projectsSelectors.js
import { createSelector } from "@reduxjs/toolkit";

export const selectProjects = (s) => s.projects.items;
export const selectTotal = (s) => s.projects.total;
export const selectStatus = (s) => s.projects.status;
export const selectError = (s) => s.projects.error;
export const selectFilters = (s) => s.projects.filters;
export const selectPage = (s) => s.projects.page;
export const selectPageSize = (s) => s.projects.pageSize;
export const selectRefreshKey = (s) => s.projects.refreshKey;

export const selectTotalPages = createSelector(
  [selectTotal, selectPageSize],
  (total, pageSize) => Math.max(1, Math.ceil(total / pageSize))
);