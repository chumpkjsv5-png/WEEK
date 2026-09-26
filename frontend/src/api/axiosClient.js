import axios from "axios";

const axiosClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

// Interceptor xử lý lỗi tập trung — áp dụng cho MỌI request dùng client này
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = "Đã có lỗi xảy ra";
    const detail = error.response?.data?.detail;

    if (Array.isArray(detail)) {
      message = detail.map((d) => d.msg).join(", ");
    } else if (typeof detail === "string") {
      message = detail;
    }

    return Promise.reject(new Error(message));
  }
);

export default axiosClient;