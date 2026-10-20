// src/features/notifications/notificationsSlice.js
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  items: []        // (1) lúc đầu chưa có thông báo nào, nên là gì?
};

const notificationsSlice = createSlice({
  name: "notifications",
  initialState,
  reducers: {
    addNotification(state, action) {
      state.items.push(action.payload);
      // (2) thêm action.payload vào state.items
    },
    removeNotification(state, action) {
      state.items = state.items.filter((n) => n.id !== action.payload);
      // (3) xoá thông báo có id = action.payload
    },
    clearNotifications(state) {
      state.items =[];
      // (4) xoá hết
    },
  },
});

export const { addNotification, removeNotification, clearNotifications } =
  notificationsSlice.actions;
export default notificationsSlice.reducer;