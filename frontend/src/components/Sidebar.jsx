import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { logout } from "../features/auth/authSlice";
import { selectUser } from "../features/auth/authSelectors";
import { LogIn, LogOut } from "lucide-react";

import "../css/Sidebar.css";

const menuItems = [
  { id: "home", label: "Home", icon: "⌂" },
  { id: "tasks", label: "Tasks", icon: "☷" },
  { id: "projects", label: "Projects", icon: "▣" },
  { id: "calendar", label: "Calendar", icon: "□" },
  { id: "knowledge", label: "Knowledge", icon: "▤" },
  { id: "notifications", label: "Notifications", icon: "♢" },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { pathname } = useLocation();
  const user = useSelector(selectUser);

  // "/" cũng được coi là Home
  const active = pathname === "/" ? "home" : pathname.split("/")[1];

  // Chữ cái đầu của tên, dùng làm avatar
  const initial = user?.full_name?.trim()?.[0]?.toUpperCase() ?? "?";

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">✓</div>
        <span>TeamHub</span>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`sidebar-item ${active === item.id ? "active" : ""}`}
            onClick={() => navigate(`/${item.id}`)}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-user">
        {user ? (
          <>
            <div className="user-avatar">{initial}</div>
            <div className="user-info">
              <strong>{user.full_name}</strong>
              <span>{user.email}</span>
              <small className="user-role">{user.role}</small>
            </div>
            <button type="button" className="logout-btn" title="Đăng xuất"
                    aria-label="Đăng xuất" onClick={() => dispatch(logout())}>
              <LogOut size={18} />
            </button>
          </>
        ) : (
          <button
            type="button"
            className="sidebar-item"
            onClick={() => navigate("/login")}
          >
            <span className="sidebar-icon">
              <LogIn size={18} />
            </span>
            <span>Đăng nhập</span>
          </button>
        )}
      </div>
    </aside>
  );
}