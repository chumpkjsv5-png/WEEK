// src/features/projects/projectsSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as projectApi from "../../api/projectApi";
import { getErrorMessage } from "../../utils/apiError";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const fetchProjects = createAsyncThunk(
  "projects/fetch",
  async (params, { signal, rejectWithValue }) => {
    try {
      const owner = params.ownerId?.trim();
      return await projectApi.getProjects(
        {
          search: params.search || undefined,
          owner_id: owner && UUID_RE.test(owner) ? owner : undefined,
          created_after: params.createdAfter || undefined,
          created_before: params.createdBefore || undefined,
          skip: (params.page - 1) * params.limit,
          limit: params.limit,
        },
        signal
      );
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const addProject = createAsyncThunk(
  "projects/add",
  async (payload, { rejectWithValue }) => {
    try {
      return await projectApi.createProject(payload);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const editProject = createAsyncThunk(
  "projects/edit",
  async ({ id, payload }, { rejectWithValue }) => {
    try {
      return await projectApi.updateProject(id, payload);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const removeProject = createAsyncThunk(
  "projects/remove",
  async (id, { rejectWithValue }) => {
    try {
      await projectApi.deleteProject(id);
      return id;
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

const initialState = {
  items: [],
  total: 0,
  status: "idle", // idle | loading | success | error
  error: null,
  filters: { search: "", ownerId: "", createdAfter: "", createdBefore: "" },
  currentPage: 1,
};

const projectsSlice = createSlice({
  name: "projects",
  initialState,
  reducers: {
    setFilter(state, action) {
      const { key, value } = action.payload;
      state.filters[key] = value;
      state.currentPage = 1;
    },
    clearFilters(state) {
      state.filters = { ...initialState.filters };
      state.currentPage = 1;
    },
    setPage(state, action) {
      state.currentPage = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjects.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        const { items, total } = action.payload;
        state.items = Array.isArray(items) ? items : [];
        state.total = total ?? 0;
        state.status = "success";

        // Xóa hết project cuối của trang cuối thì lùi về trang cuối hợp lệ
        // (currentPage đổi => useEffect ở page tự gọi lại)
        const limit = action.meta.arg.limit;
        const lastPage = Math.max(1, Math.ceil(state.total / limit));
        if (state.currentPage > lastPage) state.currentPage = lastPage;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        if (action.meta.aborted) return; // request bị hủy do đổi bộ lọc, không phải lỗi
        state.status = "error";
        state.error = action.payload ?? action.error.message;
      });
  },
});

export const { setFilter, clearFilters, setPage } = projectsSlice.actions;
export default projectsSlice.reducer;