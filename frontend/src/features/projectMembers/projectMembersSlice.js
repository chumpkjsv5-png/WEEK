// src/features/projectMembers/projectMembersSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as memberApi from "../../api/projectMemberApi";
import { getErrorMessage } from "../../utils/apiError";

export const fetchMembers = createAsyncThunk(
  "projectMembers/fetch",
  async (projectId, { signal, rejectWithValue }) => {
    try {
      return await memberApi.getProjectMembers(projectId, signal);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const addMember = createAsyncThunk(
  "projectMembers/add",
  async ({ projectId, userId }, { rejectWithValue }) => {
    try {
      return await memberApi.addProjectMember(projectId, userId);
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

export const removeMember = createAsyncThunk(
  "projectMembers/remove",
  async ({ projectId, userId }, { rejectWithValue }) => {
    try {
      return await memberApi.removeProjectMember(projectId, userId); // trả về userId
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

// Lấy (hoặc tạo) mục của một project trong store
const entryOf = (state, projectId) => {
  if (!state.byProject[projectId]) {
    state.byProject[projectId] = { items: [], status: "idle", error: null };
  }
  return state.byProject[projectId];
};

const byName = (a, b) => a.user.full_name.localeCompare(b.user.full_name);

const projectMembersSlice = createSlice({
  name: "projectMembers",
  initialState: { byProject: {} }, // { [projectId]: { items, status, error } }
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMembers.pending, (state, action) => {
        const e = entryOf(state, action.meta.arg);
        e.status = "loading";
        e.error = null;
      })
      .addCase(fetchMembers.fulfilled, (state, action) => {
        const e = entryOf(state, action.meta.arg);
        e.items = Array.isArray(action.payload) ? action.payload : [];
        e.status = "success";
      })
      .addCase(fetchMembers.rejected, (state, action) => {
        if (action.meta.aborted) return; // request bị hủy, không phải lỗi
        const e = entryOf(state, action.meta.arg);
        e.status = "error";
        e.error = action.payload ?? action.error.message;
      })
      .addCase(addMember.fulfilled, (state, action) => {
        const e = entryOf(state, action.meta.arg.projectId);
        e.items.push(action.payload);
        e.items.sort(byName);
      })
      .addCase(removeMember.fulfilled, (state, action) => {
        const e = entryOf(state, action.meta.arg.projectId);
        e.items = e.items.filter((m) => m.user_id !== action.payload);
      });
  },
});

export default projectMembersSlice.reducer;