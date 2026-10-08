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
          page: params.page,
          page_size: params.pageSize,
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
  page: 1,
  pageSize: 10,
  refreshKey: 0, // tăng lên để useEffect tải lại danh sách
};

const projectsSlice = createSlice({
  name: "projects",
  initialState,
  reducers: {
    setFilter(state, action) {
      const { key, value } = action.payload;
      state.filters[key] = value;
      state.page = 1;
    },
    clearFilters(state) {
      state.filters = { ...initialState.filters };
      state.page = 1;
    },
    setPage(state, action) {
      state.page = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProjects.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.items = Array.isArray(action.payload.items) ? action.payload.items : [];
        state.total = action.payload.total ?? 0;
        state.status = "success";

        // Xóa hết task cuối của trang cuối thì lùi về trang cuối hợp lệ
        const lastPage = Math.max(1, Math.ceil(state.total / state.pageSize));
        if (state.page > lastPage) state.page = lastPage;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        if (action.meta.aborted) return; // request bị hủy do đổi bộ lọc, không phải lỗi
        state.status = "error";
        state.error = action.payload ?? action.error.message;
      })
      // Thêm xong về trang 1; thêm/sửa/xóa xong đều yêu cầu tải lại
      .addCase(addProject.fulfilled, (state) => {
        state.page = 1;
        state.refreshKey += 1;
      })
      .addCase(editProject.fulfilled, (state) => {
        state.refreshKey += 1;
      })
      .addCase(removeProject.fulfilled, (state) => {
        state.refreshKey += 1;
      });
  },
});

export const { setFilter, clearFilters, setPage } = projectsSlice.actions;
export default projectsSlice.reducer;