// src/components/Button.jsx
import "../css/Button.css";

/**
 * Nút dùng chung.
 * - variant: "primary" | "secondary" | "danger" | "ghost"
 * - size: "sm" | "md"
 * - loading: hiện spinner và khóa nút
 * - icon: node hiển thị trước chữ (ví dụ "+" hoặc icon SVG)
 * - fullWidth: nút rộng 100%
 * Mọi prop còn lại (onClick, disabled, title, ...) được truyền thẳng xuống <button>.
 */
export default function Button({
  children,
  variant = "primary",
  size = "md",
  type = "button", // mặc định "button" để không vô tình submit form
  loading = false,
  icon = null,
  fullWidth = false,
  className = "",
  disabled = false,
  ...rest
}) {
  const classes = [
    "btn",
    `btn-${variant}`,
    `btn-${size}`,
    fullWidth ? "btn-block" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading ? <span className="btn-spinner" aria-hidden="true" /> : icon}
      {children}
    </button>
  );
}
