# Migration Plan — Week 3: priority, due_date, assignee_id

**Revision:** `ce8efeadb8fe` (down_revision `5bf6a0ec10c8`)
**Bảng ảnh hưởng:** `tasks` (tham chiếu `users`)
**Mục tiêu:** thêm 3 field mới vào task mà không mất dữ liệu cũ và không làm hỏng client cũ.

## 1. Thay đổi schema

| Field | Kiểu | Null | Default | Backfill |
|---|---|---|---|---|
| `priority` | enum `priority_enum` (`Low`, `Medium`, `High`) | NOT NULL | `server_default='Medium'` | Postgres tự điền `Medium` cho dòng cũ khi add column |
| `due_date` | `Date` | NULL | không | Không. NULL = chưa có hạn |
| `assignee_id` | UUID | NULL | không | Không. NULL = chưa giao |

Ràng buộc và index:
- FK `tasks_assignee_id_fkey`: `assignee_id` → `users.id`, `ON DELETE SET NULL`.
- Index `ix_tasks_assignee_id` (phục vụ lọc theo assignee).

## 2. Thứ tự thực hiện và lý do

| Bước | Hành động | Lý do |
|---|---|---|
| 1 | Tạo enum type `priority_enum` (`checkfirst=True`) | Cột `priority` cần type tồn tại trước |
| 2 | Add `priority` NOT NULL + `server_default='Medium'` | Dòng cũ nhận giá trị hợp lệ nên không vi phạm NOT NULL |
| 3 | Add `due_date`, `assignee_id` nullable | Không có giá trị đúng cho dữ liệu cũ nên không bịa |
| 4 | Tạo FK và index | Cột phải tồn tại trước khi gắn ràng buộc |

## 3. Quy trình chạy

1. Backup: `pg_dump` database (bắt buộc trên môi trường thật).
2. Kiểm tra version hiện tại: `alembic current` (kỳ vọng `5bf6a0ec10c8`).
3. Nâng cấp: `alembic upgrade head`.
4. Xác minh:
   - `alembic current` ra `ce8efeadb8fe (head)`.
   - Số dòng `tasks` không đổi.
   - Dòng cũ có `priority = 'Medium'`, `due_date` và `assignee_id` rỗng.
5. Deploy theo thứ tự: **DB migration → backend mới → frontend mới**.

## 4. Backward compatibility (expand → migrate → contract)

- Tuần này chỉ ở bước **expand**: thêm cột, không xóa hay đổi tên.
- Client cũ không gửi `priority` thì nhận `Medium`. Schema Pydantic cũng đặt default `Medium` và để `due_date`, `assignee_id` optional để không trả 422.
- Response có thêm field mới không làm hỏng client cũ.
- Chưa có bước contract.

## 5. Rủi ro và cách giảm

| Rủi ro | Giảm thiểu |
|---|---|
| Add NOT NULL không default trên bảng có dữ liệu sẽ lỗi | Dùng `server_default` |
| Quên tạo enum trước | Tạo enum ở bước 1 với `checkfirst=True` |
| Gõ sai giá trị enum | Dùng đúng `Low/Medium/High`, enum từ chối giá trị lạ |
| User bị xóa khi còn task được giao | `ON DELETE SET NULL`, task thành unassigned |
| Autogenerate sinh `drop_column` hoặc thiếu backfill | Đọc và sửa file migration trước khi chạy |
| Bảng lớn: add column + index có thể giữ lock | Đã test trên dữ liệu mẫu nhỏ; với bảng lớn cần cân nhắc backfill theo batch và tạo index `CONCURRENTLY` |

## 6. Kiểm thử (xem `docs/evidence/`)

- `01`–`03`: upgrade trên dữ liệu có sẵn, dòng cũ nhận `Medium`.
- `04`: insert kiểu app cũ nhận `Medium`; enum từ chối `Urgent`; FK từ chối `assignee_id` không tồn tại.
- `05`–`09`: downgrade và upgrade lại chạy được.
- `10`, `11`: chỉ có một head.
