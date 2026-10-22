import { useEffect, useRef, useState } from "react";
import { searchUsers, getUser } from "../api/userApi";

const dropdownStyle = {
  position: "absolute",
  top: "100%",
  left: 0,
  right: 0,
  margin: 0,
  padding: 0,
  listStyle: "none",
  background: "#fff",
  border: "1px solid #ccc",
  borderRadius: 4,
  maxHeight: 200,
  overflowY: "auto",
  zIndex: 10,
};

const itemStyle = { padding: "6px 10px", cursor: "pointer" };

export default function TaskFilters({
  assigneeId,
  onAssigneeIdChange,
  dueBefore,
  onDueBeforeChange,
  dueAfter,
  onDueAfterChange,
}) {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState([]);
  const [open, setOpen] = useState(false);
  const boxRef = useRef(null);

  // Tìm user khi gõ (debounce 300ms)
  useEffect(() => {
    const controller = new AbortController();
    const t = setTimeout(() => {
      searchUsers({ search: query, limit: 10 }, controller.signal)
        .then((data) => setOptions(data.items ?? []))
        .catch((err) => {
          if (err.name !== "CanceledError") console.error(err);
        });
    }, 300);
    return () => {
      clearTimeout(t);
      controller.abort();
    };
  }, [query]);

  // Có assigneeId sẵn (vd từ URL) thì lấy tên để hiển thị
  useEffect(() => {
    if (!assigneeId) return;
    const controller = new AbortController();
    getUser(assigneeId, controller.signal)
      .then((u) => setQuery(u.full_name))
      .catch((err) => {
        if (err.name !== "CanceledError") console.error(err);
      });
    return () => controller.abort();
  }, [assigneeId]);

  // Đóng dropdown khi click ra ngoài
  useEffect(() => {
    const handler = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (u) => {
    onAssigneeIdChange(String(u.id));
    setQuery(u.full_name);
    setOpen(false);
  };

  const handleClear = () => {
    onAssigneeIdChange("");
    setQuery("");
    setOpen(false);
  };

  return (
    <div className="task-filters">
      <div className="filter-field">
        <label>Assignee</label>

        {/* Wrapper chứa input + nút × + dropdown */}
        <div ref={boxRef} style={{ position: "relative" }}>
          <input
            type="text"
            placeholder="Tìm assignee..."
            value={query}
            style={{ width: "100%", paddingRight: 28, boxSizing: "border-box" }}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
              if (assigneeId) onAssigneeIdChange(""); // gõ lại thì bỏ lựa chọn cũ
            }}
            onFocus={() => setOpen(true)}
          />

          {(assigneeId || query) && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Xóa"
              style={{
                position: "absolute",
                right: 6,
                top: "50%",
                transform: "translateY(-50%)",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                fontSize: 16,
                lineHeight: 1,
                padding: 0,
                color: "#888",
              }}
            >
              ×
            </button>
          )}

          {open && (
            <ul style={dropdownStyle}>
              <li style={itemStyle} onMouseDown={handleClear}>
              </li>
              {options.map((u) => (
                <li
                  key={u.id}
                  style={itemStyle}
                  onMouseDown={() => handleSelect(u)}
                >
                  {u.full_name}
                </li>
              ))}
              {options.length === 0 && (
                <li style={{ ...itemStyle, color: "#888", cursor: "default" }}>
                </li>
              )}
            </ul>
          )}
        </div>
      </div>

      <div className="filter-field">
        <label>Due sau ngày</label>
        <input
          type="date"
          value={dueAfter ?? ""}
          onChange={(e) => onDueAfterChange(e.target.value)}
        />
      </div>

      <div className="filter-field">
        <label>Due trước ngày</label>
        <input
          type="date"
          value={dueBefore ?? ""}
          onChange={(e) => onDueBeforeChange(e.target.value)}
        />
      </div>
    </div>
  );
}