import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, useLocation } from "react-router-dom";
import { login } from "../features/auth/authSlice";
import { selectUser } from "../features/auth/authSelectors";
import "../css/LoginPage.css";

export default function LoginPage() {
  const dispatch = useDispatch();
  const user = useSelector(selectUser);
  const from = useLocation().state?.from?.pathname ?? "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Đăng nhập xong, user có giá trị thì tự chuyển trang
  if (user) return <Navigate to={from} replace />;

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setFieldErrors({});
    setSubmitting(true);
    try {
      await dispatch(login({ email, password })).unwrap();
    } catch (err) {
      if (err?.code === "validation_error") setFieldErrors(err.fields);
      else setError(err?.message ?? "Đã có lỗi xảy ra");
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit} noValidate>
        <div className="login-brand">
          <div className="login-brand-icon">✓</div>
          <span>TeamHub</span>
        </div>

        <h1 className="login-title">Đăng nhập</h1>
        <p className="login-subtitle">Chào mừng bạn quay lại</p>

        {error && (
          <div className="login-alert" role="alert">
            {error}
          </div>
        )}

        <div className="login-field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            placeholder="ban@example.com"
            autoComplete="email"
            className={fieldErrors.email ? "has-error" : ""}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {fieldErrors.email && (
            <small className="field-error" role="alert">
              {fieldErrors.email}
            </small>
          )}
        </div>

        <div className="login-field">
          <label htmlFor="password">Mật khẩu</label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            autoComplete="current-password"
            className={fieldErrors.password ? "has-error" : ""}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {fieldErrors.password && (
            <small className="field-error" role="alert">
              {fieldErrors.password}
            </small>
          )}
        </div>

        <button className="login-btn" type="submit" disabled={submitting}>
          {submitting ? "Đang đăng nhập..." : "Đăng nhập"}
        </button>
      </form>
    </div>
  );
}