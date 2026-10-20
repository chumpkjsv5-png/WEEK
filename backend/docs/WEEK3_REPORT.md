# Report Tuần 3 — Schema Change & Migration

**Mục tiêu:** Thay đổi schema mà không mất dữ liệu hiện có.
**Công cụ:** Alembic + PostgreSQL (React + FastAPI).
**Migration:** `ce8efeadb8fe` — add priority, due_date, assignee_id to tasks (down_revision `5bf6a0ec10c8`).

## 1. Đã làm

| Field | Kiểu | Null? | Default / Backfill | Lý do |
|---|---|---|---|---|
| `priority` | enum `priority_enum` (Low/Medium/High) | NOT NULL | `server_default='Medium'` | Task nào cũng có mức ưu tiên; `Medium` là giá trị trung tính |
| `due_date` | `Date` | NULL | không backfill | Task cũ thật sự chưa có hạn; NULL = "không có deadline", không bịa ngày |
| `assignee_id` | UUID, FK → `users.id`, `ON DELETE SET NULL`, có index | NULL | không backfill | Task cũ chưa có người nhận; xóa user thì task thành unassigned, không bị xóa theo |

## 2. Thứ tự migration và vì sao

1. Tạo enum type `priority_enum` trước, vì cột `priority` cần type này.
2. Thêm `priority` NOT NULL kèm `server_default='Medium'`. PostgreSQL tự điền `Medium` cho dòng cũ nên không lỗi NOT NULL. Đây là bước backfill tích hợp trong lệnh add column.
3. Thêm `due_date`, `assignee_id` dạng nullable.
4. Thêm FK và index sau cùng, khi cột đã tồn tại.
5. Downgrade chạy ngược thứ tự: index → FK → cột → drop enum type.

**Điều có thể sai:**
- Thêm cột NOT NULL không có default trên bảng có dữ liệu sẽ lỗi.
- Quên tạo enum trước khi thêm cột, hoặc quên drop enum ở downgrade, sẽ lỗi hoặc để lại type mồ côi.
- Gõ sai giá trị enum sẽ lưu sai vĩnh viễn.
- Autogenerate không viết backfill, không hiểu rename, và có thể sinh `drop_column`; vì vậy phải đọc lại file trước khi chạy.

## 3. Bằng chứng kiểm thử (`backend/docs/evidence/`)

| Kiểm tra | Kết quả |
|---|---|
| Upgrade trên dữ liệu có sẵn (`01`→`03`) | 2 task cũ được `priority = Medium`, `due_date`/`assignee_id` rỗng. Không mất dòng nào |
| Ràng buộc (`04`) | Insert task kiểu app cũ (không gửi `priority`) nhận `Medium`. Giá trị `Urgent` bị từ chối bởi enum. `assignee_id` không tồn tại bị từ chối bởi FK |
| Downgrade (`05`→`07`) | Chạy được, cấu trúc về lại như cũ, 3 dòng task còn nguyên |
| Re-upgrade (`08`→`09`) | Chạy được, nhưng mọi `priority` về `Medium`, `due_date` rỗng |
| Chuỗi revision (`10`, `11`) | Một head duy nhất `ce8efeadb8fe`, lịch sử rõ ràng |

## 4. Rollback note

- Downgrade **không mất dòng task**, nhưng **mất vĩnh viễn dữ liệu của 3 cột** `priority`, `due_date`, `assignee_id`. Bằng chứng `05` → `09`: task "Viết báo cáo" có `High` + `2026-12-31` trước downgrade, sau upgrade lại chỉ còn `Medium` và không có hạn.
- **An toàn** khi chưa ai nhập dữ liệu vào field mới, hoặc ở môi trường dev/test.
- **Không nên** downgrade trên môi trường thật khi đã có dữ liệu thật. Khi đó: backup bằng `pg_dump` trước khi upgrade, hoặc xử lý bằng migration mới (roll-forward).
- Nếu cần giữ dữ liệu trước khi downgrade, export 3 cột ra bảng hoặc file tạm.

## 5. Backward compatibility (expand → migrate → contract)

- Tuần này chỉ ở bước **expand**: thêm cột, không xóa hay đổi tên gì, nên code cũ vẫn chạy.
- Client cũ không gửi `priority` thì nhận `Medium` (default ở DB; schema Pydantic cũng cần default `Medium` và `due_date`, `assignee_id` optional để không trả 422).
- Thứ tự deploy: migrate DB → backend mới → frontend mới.
- Chưa có bước contract (chưa drop gì).

## 6. UI

- Form hỗ trợ chọn priority, due date, assignee.
- Giá trị rỗng hiển thị bằng placeholder; cần đảm bảo form gửi `null` (không phải chuỗi rỗng) cho `due_date` và `assignee_id`.
- Gợi ý cải thiện: hiển thị "Unassigned" và "No due date" thay vì chỉ gạch ngang để người dùng hiểu rõ trạng thái.

## 7. Điểm cần cập nhật / lưu ý

- `DESIGN.md` (mục 5) vẫn ghi dùng `Base.metadata.create_all()` thay vì Alembic. Cần cập nhật cho đúng thực tế.
- Thư mục `alembic/versions` hiện có chuỗi revision mới (`b4a3576240a9 initial_schema`, `61cdc7a8027f`...) trong khi bằng chứng tuần 3 dùng chuỗi cũ nằm ở `alembic/old_versions` (`5bf6a0ec10c8` → `ce8efeadb8fe`). Cần ghi chú rõ chuỗi nào là chuỗi hiện hành và vì sao đã gộp lại.
- Evidence được kiểm trên 2-3 dòng mẫu, chưa thử với khối lượng lớn nên chưa đánh giá lock hoặc backfill theo batch.
- Chưa có tài liệu ERD v3 và migration plan dạng file riêng trong `docs/` (ngoài `WEEK3_REPORT.md` này).

## 8. Điều đã học

- Thứ tự migration: type → cột → ràng buộc và index; downgrade theo thứ tự ngược lại.
- Backfill: chỉ điền khi có giá trị đúng; không có giá trị đúng thì để NULL.
- `ON DELETE SET NULL` phù hợp cho FK nullable; `CASCADE` sẽ xóa task theo user, không phù hợp.
- Autogenerate chỉ là bản nháp, luôn phải đọc lại và tự viết backfill.
- Downgrade có thể mất dữ liệu cột bị drop; cần backup và rollback note.
