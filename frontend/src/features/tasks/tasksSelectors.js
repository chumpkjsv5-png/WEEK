// src/features/tasks/tasksSelectors.js
import { createSelector } from "@reduxjs/toolkit";
export const ITEMS_PER_PAGE = 5;

export const selectFilters = (s) => s.tasks.filters;
export const selectStatus = (s) => s.tasks.status;
export const selectError = (s) => s.tasks.error;
export const selectCurrentPage = (s) => s.tasks.currentPage;
export const selectAllTasks = (s) => s.tasks.items;

export const selectTotalPages = (s) =>
  Math.ceil(s.tasks.items.length / ITEMS_PER_PAGE);

export const selectPaginatedTasks = createSelector(
  [selectAllTasks, selectCurrentPage],
  (items, page) => {
    const start = (page - 1) * ITEMS_PER_PAGE;
    return items.slice(start, start + ITEMS_PER_PAGE);
  }
);