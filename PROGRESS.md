# PROGRESS: Học Redux qua dự án WEEK/frontend

## 1. Tóm tắt phiên học

Học Redux Toolkit từ cơ bản, dựa trên code thật của dự án (app quản lý Task/Project, React 19 + `@reduxjs/toolkit` 2 + `react-redux` 9). Sau đó tự thực hành viết một slice mới.

### Code thật đã đọc
- `src/main.jsx`: `<Provider store={store}>`
- `src/app/store.js`: `configureStore` gom các slice
- `src/features/tasks/tasksSlice.js`, `tasksSelectors.js`: slice, thunk, selector
- `src/features/projectMembers/projectMembersSlice.js`: state dạng `byProject`
- `src/pages/TasksPage.jsx`: `useSelector`, `useDispatch`, `.unwrap()`, `abort`
- `src/api/taskApi.js`, `axiosClient.js`: lớp gọi API (không biết gì về Redux)

### Bài học đã đi qua

| Bài | Nội dung | Kết quả |
|---|---|---|
| 1-2 | Store, Action, Dispatch, Reducer, Selector | Nắm vững |
| 3 | `createAsyncThunk`: `pending`, `fulfilled`, `rejected` | Nắm vững, từng nhầm vai trò của `payload` ở `rejected` |
| 4 | `.unwrap()`, `try/catch`, vì sao sửa xong phải `load()` lại | Nắm vững |
| Thực hành | Viết `notificationsSlice`, đăng ký store, dùng trong component | Hoàn thành code, build qua |

## 2. Các khái niệm cốt lõi (bản nhớ nhanh)

```
ĐỌC:  useSelector(state => state.<ngăn>.<trường>)
GHI:  dispatch(action) → reducer sửa state → kho đổi → useSelector thấy → component vẽ lại
```

| Khái niệm | Ví dụ ngân hàng | Trong code |
|---|---|---|
| Store | Két sắt | `configureStore` trong `store.js` |
| Action | Tờ phiếu | `{ type: "tasks/setPage", payload: 2 }` |
| Dispatch | Nộp phiếu | `dispatch(setPage(2))` |
| Reducer | Nhân viên sửa sổ | `setPage(state, action) { ... }` trong slice |
| Selector | Xem sổ | `useSelector(...)` |
| Payload | Dữ liệu ghi trên phiếu | Thứ nằm trong ngoặc: `removeNotification(2)` thì payload là `2` |

### Điểm hay nhầm (đã rút ra từ phiên học)
- **`payload` chỉ là dữ liệu MỚI gửi lên**, không chứa dữ liệu cũ. Reducer mới là nơi ghép cũ với mới.
- **Chỉ có reducer sửa state**, `dispatch` chỉ đưa phiếu.
- Thunk luôn phát `pending`, rồi **một trong hai** `fulfilled` hoặc `rejected`, không bao giờ cả hai.
- `dispatch(thunk)` **không ném lỗi** khi API lỗi. Phải `.unwrap()` mới `try/catch` được.
- Dữ liệu do backend sắp xếp, lọc, đếm thì **tải lại** (`load()`), đừng tự sửa `items` ở frontend.
- Trong `reducer: { notificationsReducer }` (viết tắt) tên ngăn thành `notificationsReducer`. Phải viết `notifications: notificationsReducer`.
- Tên trường ở chỗ thêm và chỗ xoá phải trùng nhau (`id`), nếu không `filter` âm thầm không xoá gì.

## 3. Cách học đã dùng (nên lặp lại)

1. **Học theo code thật của dự án** thay vì ví dụ trừu tượng.
2. **Một ý mỗi bước**, dùng ví dụ ngân hàng để gắn hình ảnh.
3. **Câu hỏi kiểm tra sau mỗi bài** (2-3 câu), trả lời bằng lời của mình. Sai thì được sửa ngay.
4. **Thực hành theo khung sườn** có chỗ `___`, kèm gợi ý nhỏ dần: gợi ý, rồi hướng dẫn từng bước, rồi mới đáp án.
5. **Kiểm tra file thật sau mỗi lần "xong"** (đọc file, chạy `npm run build`, `oxlint`). Không chấm theo lời nói.
6. Sửa lại từ ngữ cho chính xác (ví dụ "payload", "action", "state") vì dùng sai từ dẫn tới hiểu sai.

## 4. Tình trạng thực hành `notifications`

Đã có:
- `src/features/notifications/notificationsSlice.js` (state `items`, 3 reducer: thêm, xoá theo id, xoá hết)
- `src/app/store.js` có `notifications: notificationsReducer`
- `src/components/NotificationDemo.jsx` (đọc bằng `useSelector`, gửi bằng `dispatch`)
- `src/App.jsx` có route `/NotificationDemo`

Đã kiểm tra: code đúng, `npm run build` thành công, lint không báo lỗi ở file mới.

**Chưa kiểm tra:** chạy thật trên trình duyệt (`npm run dev`, vào `/NotificationDemo`, bấm 3 nút). Cần tự thử.

### Việc cần dọn
- `TEST.js` (ở `frontend/`) là bản nháp, xoá nếu không dùng.
- Route `/NotificationDemo` và import `NotificationDemo` trong `App.jsx` chỉ để học, xoá trước khi commit nếu không cần giữ.
- Chạy `npm run build` có cập nhật thư mục `dist/`.

## 5. Bước tiếp theo

- **A.** Nối vào app thật: thêm task thành công thì tự hiện thông báo (dùng `extraReducers`, các slice phối hợp với nhau).
- **B.** `createSelector`: tính dữ liệu từ kho (ví dụ đếm task theo status) không bị tính lại thừa.
- **C.** Đọc tiếp `projectsSlice.js` và `ProjectsPage.jsx` để so sánh với `tasks`.

Điểm cần chắc lại: vai trò `payload` của `rejected` (lưu câu lỗi vào `state.error`), và việc `type` có dạng `"tên_slice/tên_reducer"`.
