import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import * as authApi from "../../api/authApi";
import { TOKEN_KEY } from "../../api/axiosClient";

// ApiError không serialize được nên chỉ đưa object thường vào rejectWithValue
const toPayload = (err) => ({
  code: err.code,
  message: err.message,
  fields: err.fields ?? {},
});

export const login = createAsyncThunk(
  "auth/login",
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const { access_token } = await authApi.login(email, password);
      localStorage.setItem(TOKEN_KEY, access_token);
      return await authApi.getMe();
    } catch (err) {
      localStorage.removeItem(TOKEN_KEY);
      return rejectWithValue(toPayload(err));
    }
  }
);

export const fetchMe = createAsyncThunk("auth/fetchMe", async (_, { rejectWithValue }) => {
  try {
    return await authApi.getMe();
  } catch (err) {
    return rejectWithValue(toPayload(err));
  }
});

export const logout = createAsyncThunk("auth/logout", async () => {
  try {
    await authApi.logout();
  } catch {
    /* bỏ qua, vẫn xoá token ở client */
  }
  localStorage.removeItem(TOKEN_KEY);
});

const authSlice = createSlice({
  name: "auth",
  initialState: {
    user: null,
    loading: !!localStorage.getItem(TOKEN_KEY), // đang chờ /auth/me khi mở app
  },
  reducers: {
    clearAuth(state) {
      state.user = null;
      state.loading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.fulfilled, (state, { payload }) => {
        state.user = payload;
      })
      .addCase(fetchMe.fulfilled, (state, { payload }) => {
        state.user = payload;
        state.loading = false;
      })
      .addCase(fetchMe.rejected, (state) => {
        state.user = null;
        state.loading = false;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
      });
  },
});

export const { clearAuth } = authSlice.actions;
export default authSlice.reducer;