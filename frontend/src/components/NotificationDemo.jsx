import { useSelector, useDispatch } from "react-redux";
import {
  addNotification,
  removeNotification,
  clearNotifications,
} from "../features/notifications/notificationsSlice";

export default function NotificationDemo() {
  const dispatch = useDispatch();

  // (A) ĐỌC danh sách thông báo từ kho
  const items = useSelector((state) => state.notifications.items);

  return (
    <div>
      {/* (B) nút thêm: gửi phiếu có id và message */}
      <button
        onClick={() =>
          dispatch(addNotification({ id: Date.now(), message: "Xin chào!" }))
        }
      >
        Thêm thông báo
      </button>

      {/* (C) nút xoá hết */}   
      <button onClick={() => dispatch(clearNotifications())}>Xoá hết</button>

      <ul>
        {items.map((n) => (
          <li key={n.id}>
            {n.message}
            {/* (D) nút xoá một cái: payload là id */}
            <button onClick={() => dispatch(removeNotification(n.id))}>Xoá</button>
          </li>
        ))}
      </ul>
    </div>
  );
}