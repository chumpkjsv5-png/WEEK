# Rollback Note — Week 3 (`ce8efeadb8fe`)

## 1. Lệnh

- Xem version hiện tại: `alembic current`
- Lùi một bước: `alembic downgrade -1` (về `5bf6a0ec10c8`)
- Nâng lại: `alembic upgrade head`

## 2. Downgrade làm gì

Thứ tự ngược với upgrade:
1. Drop index `ix_tasks_assignee_id`
2. Drop FK `tasks_assignee_id_fkey`
3. Drop cột `assignee_id`, `due_date`, `priority`
4. Drop enum type `priority_enum`

## 3. Dữ liệu bị mất

| Mất | Giữ |
|---|---|
| Toàn bộ giá trị `priority`, `due_date`, `assignee_id` | Các dòng task và các cột cũ (`id`, `title`, ...) |

Bằng chứng (`docs/evidence/05`–`09`): task "Viết báo cáo" có `High` + `2026-12-31` trước downgrade; sau downgrade rồi upgrade lại chỉ còn `Medium` và không có hạn. Upgrade lại **không khôi phục** giá trị đã nhập.

## 4. Khi nào an toàn

| Tình huống | Downgrade |
|---|---|
| Dev/test, hoặc vừa upgrade và chưa ai nhập field mới | An toàn |
| Production, đã có người dùng field mới | **Không nên.** Mất dữ liệu thật |

## 5. Quy trình rollback trên môi trường thật

1. Backup trước khi upgrade (`pg_dump`) và giữ file backup.
2. Nếu phải downgrade khi đã có dữ liệu mới, export trước 3 cột:
   `COPY (SELECT id, priority, due_date, assignee_id FROM tasks) TO ... CSV`
3. Chạy `alembic downgrade -1`, kiểm tra `alembic current` và số dòng `tasks`.
4. Rollback **code** về bản trước (backend và frontend). Vì migration chỉ thêm cột nên code cũ chạy được cả trước và sau downgrade.
5. Khi sửa lại xong, nâng lại bằng `alembic upgrade head`, rồi import lại dữ liệu đã export nếu cần.

## 6. Ưu tiên roll-forward

Nếu lỗi nằm ở logic hoặc dữ liệu (không phải cấu trúc), nên sửa bằng migration mới thay vì downgrade, để không mất dữ liệu người dùng đã nhập.

## 7. Kiểm tra sau rollback

- `alembic current` ra `5bf6a0ec10c8`.
- Số dòng `tasks` không đổi.
- Bảng `tasks` không còn 3 cột mới; type `priority_enum` đã bị xóa.
- App cũ tạo, sửa, xóa task bình thường.
