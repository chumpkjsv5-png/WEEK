import axios from "axios";

export const TOKEN_KEY = "token";
export const UNAUTHORIZED_EVENT = "auth:unauthorized";

const axiosClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

// ApiError kế thừa Error nên code cũ dùng err.message vẫn chạy bình thường
export class ApiError extends Error {
  constructor({ status, code, message, fields }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields ?? {};
  }
}

const FRIENDLY = {

  403: "Bạn không có quyền thực hiện thao tác này.",
  404: "Không tìm thấy dữ liệu bạn yêu cầu.",
  409: "Dữ liệu bị xung đột với dữ liệu hiện có.",
  422: "Dữ liệu không hợp lệ.",
  500: "Máy chủ gặp lỗi. Vui lòng thử lại sau.",
};

// Gắn token vào mọi request
axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Xử lý lỗi tập trung: mọi lỗi đều thành ApiError
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Request bị huỷ bằng signal: giữ nguyên để nơi gọi bỏ qua bằng axios.isCancel
    if (axios.isCancel(error)) return Promise.reject(error);

    // Không có response: mất mạng, server tắt, CORS chặn...
    if (!error.response) {
      return Promise.reject(
        new ApiError({
          status: 0,
          code: "network_error",
          message: "Không kết nối được tới máy chủ. Kiểm tra lại mạng.",
        })
      );
    }

    const { status, data } = error.response;
    const e = data?.detail ?? data?.error;

    // Dự phòng shape cũ { detail } phòng khi có lỗi không đi qua handler
    let legacy;
    if (Array.isArray(data?.detail)) legacy = data.detail.map((d) => d.msg).join(", ");
    else if (typeof data?.detail === "string") legacy = data.detail;

    const apiError = new ApiError({
      status,
      code: e?.code ?? "error",
      message: e?.message ?? legacy ?? FRIENDLY[status] ?? "Đã có lỗi xảy ra",
      fields: e?.fields,
    });

    const isLogin = error.config?.url?.includes("/auth/login");

    if (status === 401 && !isLogin && apiError.code === "UNAUTHORIZED") {
      if (apiError.code === "TOKEN_EXPIRED") {
        // Token hết hạn: xóa token và yêu cầu đăng nhập lại.
        // Nếu sau này có refresh token, xử lý refresh tại đây.
        localStorage.removeItem(TOKEN_KEY);
        window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
      } else if (
        apiError.code === "AUTHENTICATION_REQUIRED" ||
        apiError.code === "INVALID_TOKEN"
      ) {
        localStorage.removeItem(TOKEN_KEY);
        window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
      }
    }

    return Promise.reject(apiError);
  }
);

export default axiosClient;