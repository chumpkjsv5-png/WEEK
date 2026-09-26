export const TASK_STATUS = {
  PENDING: "pending",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
};

export const TASK_STATUS_OPTIONS = [
  { value: TASK_STATUS.PENDING, label: "Chưa làm" },
  { value: TASK_STATUS.IN_PROGRESS, label: "Đang làm" },
  { value: TASK_STATUS.COMPLETED, label: "Hoàn thành" },
];

export const TASK_STATUS_LABEL = {
  [TASK_STATUS.PENDING]: "Chưa làm",
  [TASK_STATUS.IN_PROGRESS]: "Đang làm",
  [TASK_STATUS.COMPLETED]: "Hoàn thành",
};