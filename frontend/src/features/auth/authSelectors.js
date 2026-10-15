export const selectUser = (state) => state.auth.user;
export const selectAuthLoading = (state) => state.auth.loading;
export const selectRole = (state) => state.auth.user?.role ?? null;
