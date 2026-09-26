import { useState } from "react";

const menuItems = [
  {
    id: "home",
    label: "Home",
    icon: "⌂",
  },
  {
    id: "tasks",
    label: "Tasks",
    icon: "☷",
  },
  {
    id: "projects",
    label: "Projects",
    icon: "▣",
  },
  {
    id: "calendar",
    label: "Calendar",
    icon: "□",
  },
  {
    id: "knowledge",
    label: "Knowledge",
    icon: "▤",
  },
  {
    id: "notifications",
    label: "Notifications",
    icon: "♢",
  },
];

export default function Sidebar() {
  const [active, setActive] = useState("tasks");

  return (
    <aside className="sidebar">

      <div className="brand">

        <div className="brand-icon">
          ✓
        </div>

        <span>TeamHub</span>

      </div>

      <nav className="sidebar-nav">

        {menuItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`sidebar-item ${
              active === item.id ? "active" : ""
            }`}
            onClick={() => setActive(item.id)}
          >

            <span className="sidebar-icon">
              {item.icon}
            </span>

            <span>
              {item.label}
            </span>

          </button>
        ))}

      </nav>

      <div className="sidebar-user">

        <div className="user-avatar">
          A
        </div>

        <div className="user-info">
          <strong>Andy</strong>
          <span>andy@example.com</span>
        </div>

      </div>

    </aside>
  );
}