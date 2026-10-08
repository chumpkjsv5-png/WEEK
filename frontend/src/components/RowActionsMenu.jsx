// src/components/RowActionsMenu.jsx
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export default function RowActionsMenu({ items }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const menuRef = useRef(null);

  // Tính vị trí ngay sau khi menu được vẽ, trước khi trình duyệt hiển thị
  useLayoutEffect(() => {
    if (!open || !triggerRef.current || !menuRef.current) return;

    const t = triggerRef.current.getBoundingClientRect();
    const m = menuRef.current.getBoundingClientRect();
    const gap = 4;

    let top = t.bottom + gap;
    if (top + m.height > window.innerHeight - 8) {
      top = t.top - m.height - gap; // không đủ chỗ phía dưới thì lật lên trên
    }

    let left = t.right - m.width;   // canh mép phải menu với mép phải nút
    if (left < 8) left = 8;

    setPos({ top: Math.max(8, top), left });
  }, [open]);

  // Đóng khi bấm ra ngoài, nhấn Escape, cuộn hoặc đổi kích thước cửa sổ
  useEffect(() => {
    if (!open) return;

    const close = () => setOpen(false);
    const onMouseDown = (e) => {
      if (
        triggerRef.current?.contains(e.target) ||
        menuRef.current?.contains(e.target)
      ) {
        return;
      }
      setOpen(false);
    };
    const onKeyDown = (e) => {
      if (e.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", onMouseDown);
    document.addEventListener("keydown", onKeyDown);
    window.addEventListener("resize", close);
    window.addEventListener("scroll", close, true); // true: bắt cả cuộn trong container con

    return () => {
      document.removeEventListener("mousedown", onMouseDown);
      document.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("resize", close);
      window.removeEventListener("scroll", close, true);
    };
  }, [open]);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className="row-menu-trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        title="Thao tác khác"
        onClick={() => setOpen((o) => !o)}
      >
        ⋯
      </button>

      {open &&
        createPortal(
          <ul
            ref={menuRef}
            className="row-menu-list"
            role="menu"
            style={{ top: pos.top, left: pos.left }}
          >
            {items.map((item) => (
              <li key={item.label} role="none">
                <button
                  type="button"
                  role="menuitem"
                  className={`row-menu-item ${item.danger ? "danger" : ""}`}
                  onClick={() => {
                    setOpen(false);
                    item.onClick();
                  }}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>,
          document.body
        )}
    </>
  );
}