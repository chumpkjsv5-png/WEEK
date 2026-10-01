// src/features/tasks/tasksSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as taskApi from "../../api/taskApi"; // đổi theo file API của bạn

const toMessage = (err) => err?.message || "Có lỗi xảy ra";

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
      });
    } catch (err) {
      return rejectWithValue(toMessage(err));
    }
  }
);

export const addTask = createAsyncThunk(
  "tasks/add",
  async (payload, { rejectWithValue }) => {
    try {
      return await taskApi.createTask(payload);
    } catch (err) {
      return rejectWithValue(toMessage(err));
    }
  }
);

export const editTask = createAsyncThunk(
  "tasks/edit",
  async ({ id, payload }, { rejectWithValue }) => {
    try {
      return await taskApi.updateTask(id, payload);
    } catch (err) {
      return rejectWithValue(toMessage(err));
    }
  }
);

export const finishTask = createAsyncThunk(
  "tasks/finish",
  async (id, { rejectWithValue }) => {
    try {
      return await taskApi.completeTask(id);
    } catch (err) {
      return rejectWithValue(toMessage(err));
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
      return rejectWithValue(toMessage(err));
    }
  }
);

const initialState = {
  items: [],
  total: 0,
  status: "idle", // idle | loading | succeeded | failed
  error: null,
  filters: {
    search: "",
    statusFilter: "",
    priorityFilter: "",
    assigneeId: "",
    dueBefore: "",
    dueAfter: "",
  },
  currentPage: 1,
};

const replaceById = (state, action) => {
  const i = state.items.findIndex((t) => t.id === action.payload.id);
  if (i !== -1) state.items[i] = action.payload;
};

const tasksSlice = createSlice({
  name: "tasks",
  initialState,
  reducers: {
    setFilter(state, action) {
      const { key, value } = action.payload;
      state.filters[key] = value;
      state.currentPage = 1;
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
        })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.status = "error";
        state.error = action.payload ?? action.error.message;
      })
      .addCase(addTask.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(editTask.fulfilled, replaceById)
      .addCase(finishTask.fulfilled, replaceById)
      .addCase(removeTask.fulfilled, (state, action) => {
        state.items = state.items.filter((t) => t.id !== action.payload);
      });
  },
});

export const { setFilter, clearFilters, setPage } = tasksSlice.actions;
export default tasksSlice.reducer;