// src/features/projects/projectsSelectors.js

// Số project mỗi trang (phải <= MAX_LIMIT = 100 của backend)
export const ITEMS_PER_PAGE = 10;

export const selectFilters = (s) => s.projects.filters;
export const selectStatus = (s) => s.projects.status;
export const selectError = (s) => s.projects.error;
export const selectCurrentPage = (s) => s.projects.currentPage;

// Project của trang hiện tại (backend đã cắt sẵn)
export const selectProjects = (s) => s.projects.items;

// Tổng số project khớp bộ lọc (lấy từ backend, không phải items.length)
export const selectTotal = (s) => s.projects.total;

export const selectTotalPages = (s) =>
  Math.max(1, Math.ceil(s.projects.total / ITEMS_PER_PAGE));