import { useEffect, useRef, useState } from "react";
import axios from "axios";
import useDebounce from "../hooks/useDebounce";
import { getUser, searchUsers } from "../api/userApi";
import "../css/UserSelect.css";

export default function UserSelect({
  value,                       // id user đang chọn ("" nếu chưa chọn)
  onChange,                    // (id: string) => void
  placeholder = "Tìm theo tên hoặc email...",
  disabled = false,
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null); // {id, full_name, email}
  const boxRef = useRef(null);

  const debouncedQuery = useDebounce(query, 300);

  // Lấy thông tin người đang chọn (khi chỉ có id, ví dụ mở form sửa)
  useEffect(() => {
    if (!value) {
      setSelected(null);
      return;
    }
    if (selected?.id === value) return;
    const controller = new AbortController();
    getUser(value, controller.signal)
      .then(setSelected)
      .catch((err) => {
        if (!axios.isCancel(err)) setSelected({ id: value, full_name: "Không rõ", email: "" });
      });
    return () => controller.abort();
  }, [value]); // eslint-disable-line react-hooks/exhaustive-deps

  // Tìm user khi mở dropdown hoặc khi gõ
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setLoading(true);
    searchUsers({ search: debouncedQuery }, controller.signal)
      .then((data) => setOptions(data.items ?? []))
      .catch((err) => {
        if (!axios.isCancel(err)) setOptions([]);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [open, debouncedQuery]);

  // Bấm ra ngoài thì đóng
  useEffect(() => {
    function onClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  function choose(user) {
    setSelected(user);
    onChange(user.id);
    setQuery("");
    setOpen(false);
  }

  function clear(e) {
    e.stopPropagation();
    setSelected(null);
    onChange("");
    setQuery("");
  }

  return (
    <div className="user-select" ref={boxRef}>
      {/* Đã chọn và đang đóng: hiện tên + email */}
      {selected && !open ? (
        <button
          type="button"
          className="user-select-value"
          onClick={() => !disabled && setOpen(true)}
          disabled={disabled}
        >
          <span className="user-select-text">
            <strong>{selected.full_name}</strong>
            <small>{selected.email}</small>
          </span>
          {!disabled && (
            <span className="user-select-clear" onClick={clear} title="Bỏ chọn">
              ×
            </span>
          )}
        </button>
      ) : (
        <input
          className="user-select-input"
          value={query}
          placeholder={placeholder}
          disabled={disabled}
          onFocus={() => setOpen(true)}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          autoFocus={open && !!selected}
        />
      )}

      {open && (
        <ul className="user-select-menu" role="listbox">
          {loading && <li className="user-select-note">Đang tìm...</li>}
          {!loading && options.length === 0 && (
            <li className="user-select-note">Không tìm thấy user</li>
          )}
          {options.map((u) => (
            <li
              key={u.id}
              role="option"
              aria-selected={u.id === value}
              className={`user-select-option ${u.id === value ? "active" : ""}`}
              onMouseDown={(e) => {
                e.preventDefault(); // không cho input mất focus trước khi chọn
                choose(u);
              }}
            >
              <strong>{u.full_name}</strong>
              <small>{u.email}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}