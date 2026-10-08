// src/features/projectMembers/projectMembersSelectors.js
const EMPTY_LIST = [];                                   // hằng số, tránh tạo mảng mới mỗi lần render
const EMPTY_ENTRY = { items: EMPTY_LIST, status: "idle", error: null };

const entry = (s, projectId) => s.projectMembers.byProject[projectId] ?? EMPTY_ENTRY;

export const selectMembers = (s, projectId) => entry(s, projectId).items;
export const selectMembersStatus = (s, projectId) => entry(s, projectId).status;
export const selectMembersError = (s, projectId) => entry(s, projectId).error;