// src/features/tasks/tasksSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as taskApi from "../../api/taskApi";
import { getErrorMessage } from "../../utils/apiError";

export const fetchTasks = createAsyncThunk(
  "tasks/fetch",
  async (params, { rejectWithValue }) => {
    try {
      return await taskApi.getTasks({
        projectId: params.projectId,
        search: params.search,
        status: params.statusFilter,
        priority: params.priorityFilter,
        assigneeId: params.assigneeId,
        dueBefore: params.dueBefore,
        dueAfter: params.dueAfter,
        sortByPriority: params.sortByPriority,
        skip: (params.page - 1) * params.limit, // Chuyển trang thành số bản ghi cần bỏ qua
        limit: params.limit,
      });
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const addTask = createAsyncThunk(
  "tasks/add",
  async (payload, { rejectWithValue }) => {
    try {
      return await taskApi.createTask(payload);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const editTask = createAsyncThunk(
  "tasks/edit",
  async ({ id, payload }, { rejectWithValue }) => {
    try {
      return await taskApi.updateTask(id, payload);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const finishTask = createAsyncThunk(
  "tasks/finish",
  async (id, { rejectWithValue }) => {
    try {
      return await taskApi.completeTask(id);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const removeTask = createAsyncThunk(
  "tasks/remove",
  async (id, { rejectWithValue }) => {
    try {
      await taskApi.deleteTask(id);
      return id;
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

const initialState = {
  items: [], // Chỉ chứa task của trang hiện tại
  total: 0, // Tổng số task khớp bộ lọc từ backend
  status: "idle", // idle | loading | success | error
  error: null,
  filters: {
    search: "",
    statusFilter: "",
    priorityFilter: "",
    assigneeId: "",
    dueBefore: "",
    dueAfter: "",
    sortByPriority: false,
  },
  currentPage: 1,
};

const tasksSlice = createSlice({
  name: "tasks",
  initialState,
  reducers: {
    setFilter(state, action) {
      const { key, value } = action.payload;
      state.filters[key] = value;
      state.currentPage = 1; // Thay đổi bộ lọc thì quay về trang 1
    },

    clearFilters(state) {
      state.filters.priorityFilter = "";
      state.filters.assigneeId = "";
      state.filters.dueBefore = "";
      state.filters.dueAfter = "";
      state.currentPage = 1;
    },

    setPage(state, action) {
      state.currentPage = action.payload;
    },
  },

  // Sau khi thêm/sửa/hoàn thành/xóa task, component gọi lại fetchTasks
  // để backend quyết định thứ tự và tổng số bản ghi.
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })

      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.status = "success";
        state.items = action.payload.items ?? [];
        state.total = action.payload.total ?? 0;

        // Nếu trang hiện tại vượt quá trang cuối, chuyển về trang cuối
        const limit = action.meta.arg.limit;
        const totalPages = Math.max(
          1,
          Math.ceil(state.total / limit)
        );

        if (state.currentPage > totalPages) {
          state.currentPage = totalPages;
        }
      })

      .addCase(fetchTasks.rejected, (state, action) => {
        if (action.meta.aborted) return; // Bỏ qua request đã bị hủy

        state.status = "error";
        state.error = action.payload ?? action.error.message;
      });
  },
});

export const { setFilter, clearFilters, setPage } = tasksSlice.actions;

export default tasksSlice.reducer;
