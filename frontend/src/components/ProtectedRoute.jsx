import { useSelector } from "react-redux";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { selectAuthLoading, selectUser } from "../features/auth/authSelectors";

export default function ProtectedRoute({ roles }) {
  const user = useSelector(selectUser);
  const loading = useSelector(selectAuthLoading);
  const location = useLocation();

  if (loading) return <p>Đang tải...</p>;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  if (roles && !roles.includes(user.role)) {
    return <p role="alert">Bạn không có quyền truy cập trang này.</p>;
  }
  return <Outlet />;
}