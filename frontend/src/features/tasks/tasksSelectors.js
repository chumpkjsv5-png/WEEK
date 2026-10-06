// src/features/tasks/tasksSelectors.js

// Số task mỗi trang (phải <= MAX_LIMIT = 100 của backend)
export const ITEMS_PER_PAGE = 5;

export const selectFilters = (s) => s.tasks.filters;
export const selectStatus = (s) => s.tasks.status;
export const selectError = (s) => s.tasks.error;
export const selectCurrentPage = (s) => s.tasks.currentPage;

// Task của trang hiện tại (backend đã cắt sẵn)
export const selectTasks = (s) => s.tasks.items;

// Tổng số task khớp bộ lọc (lấy từ backend, không phải items.length)
export const selectTotal = (s) => s.tasks.total;

export const selectTotalPages = (s) =>
  Math.max(1, Math.ceil(s.tasks.total / ITEMS_PER_PAGE));