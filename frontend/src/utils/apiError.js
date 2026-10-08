// src/utils/apiError.js
export const getErrorMessage = (err) => {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;                 // 404, 409, 400
  if (Array.isArray(detail))                                      // 422 của Pydantic
    return detail.map((d) => `${d.loc?.slice(1).join(".")}: ${d.msg}`).join("; ");
  return err?.message || "Có lỗi xảy ra";
};