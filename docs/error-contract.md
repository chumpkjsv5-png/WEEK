mkdir -p docs
cat > docs/error-contract.md << 'EOF'
# Error contract

Hợp đồng giữa backend và client về cách báo lỗi. Client phân nhánh theo
**HTTP status** và **`code`**, không phân tích `message`.

## 1. Định dạng

    {
      "detail": {
        "code": "TASK_NOT_FOUND",
        "message": "Task không tồn tại"
      }
    }

Quy ước:

- `code`: chuỗi cố định dạng `SCREAMING_SNAKE_CASE`. Đã công bố thì không đổi tên.
- `message`: câu tiếng Việt cho người đọc, có thể đổi nội dung bất cứ lúc nào.
- Không bao giờ trả stack trace hay chi tiết nội bộ. Lỗi không lường trước chỉ trả
  `INTERNAL_SERVER_ERROR`, chi tiết nằm trong log server.
- Mọi lỗi nghiệp vụ là `AppError` (`app/core/exceptions.py`), được dịch sang JSON bởi
  một handler duy nhất trong `main.py`.

## 2. Bảng ánh xạ HTTP status

| Status | Lớp lỗi | Mã mặc định | Ý nghĩa |
|---|---|---|---|
| 400 | `BadRequestError` | `BAD_REQUEST` | Dữ liệu hợp lệ về cú pháp nhưng sai nghiệp vụ |
| 401 | `UnauthorizedError` | `UNAUTHORIZED` | Chưa đăng nhập hoặc thông tin xác thực không hợp lệ |
| 403 | `ForbiddenError` | `FORBIDDEN` | Đã đăng nhập nhưng không đủ quyền |
| 404 | `NotFoundError` | `NOT_FOUND` | Tài nguyên không tồn tại |
| 409 | `ConflictError` | `CONFLICT` | Xung đột trạng thái hiện tại |
| 422 | (FastAPI) | không có | Dữ liệu gửi lên sai định dạng, xem mục 4 |
| 500 | `InternalServerError` | `INTERNAL_SERVER_ERROR` | Lỗi hệ thống |
| 500 | `ContentMissingError` | `CONTENT_MISSING` | Dữ liệu bị lệch giữa hai kho, xem mục 5 |
| 503 | `StoreUnavailableError` | `STORE_UNAVAILABLE` | Một kho dữ liệu tạm không dùng được |

## 3. Danh mục mã lỗi

### Chung

| Code | Status | Khi nào |
|---|---|---|
| `INTERNAL_SERVER_ERROR` | 500 | Lỗi không lường trước |

### Articles

| Code | Status | Khi nào |
|---|---|---|
| `ARTICLE_NOT_FOUND` | 404 | Bài không tồn tại, hoặc chưa ở trạng thái `published` |
| `CONTENT_MISSING` | 500 | Có metadata ở SQL nhưng thiếu nội dung ở Mongo |
| `STORE_UNAVAILABLE` | 503 | Ghi hoặc đọc Mongo thất bại |

### Tasks

| Code | Status | Khi nào |
|---|---|---|
| `TASK_NOT_FOUND` | 404 | Task không tồn tại |
| `PROJECT_NOT_FOUND` | 404 | `project_id` không tồn tại |
| `ASSIGNEE_NOT_FOUND` | 404 | `assignee_id` không tồn tại |
| `ASSIGNEE_NOT_PROJECT_MEMBER` | 400 | Người được giao không thuộc project |
| `TASK_NOT_ASSIGNED_TO_YOU` | 403 | Member thao tác trên task không giao cho mình |
| `TASK_STATUS_ONLY` | 403 | Member sửa trường khác ngoài `status` |

### Projects

| Code | Status | Khi nào |
|---|---|---|
| `PROJECT_NOT_FOUND` | 404 | Project không tồn tại |
| `PROJECT_FORBIDDEN` | 403 | Sửa hoặc xóa project của người khác |
| `PROJECT_OWNER_CHANGE_FORBIDDEN` | 403 | Không phải admin mà đổi chủ sở hữu |
| `OWNER_NOT_FOUND` | 400 | `owner_id` mới không tồn tại |

### Project members

| Code | Status | Khi nào |
|---|---|---|
| `PROJECT_MEMBER_FORBIDDEN` | 403 | Quản lý thành viên của project không phải của mình |
| `USER_NOT_FOUND` | 404 | User cần thêm không tồn tại |
| `MEMBER_NOT_FOUND` | 404 | User không phải thành viên |
| `MEMBER_ALREADY_EXISTS` | 409 | User đã là thành viên |
| `CANNOT_REMOVE_OWNER` | 409 | Gỡ chủ sở hữu khỏi project |
| `MEMBER_HAS_OPEN_TASKS` | 409 | Gỡ thành viên còn task chưa hoàn thành |

### Users

| Code | Status | Khi nào |
|---|---|---|
| `USER_NOT_FOUND` | 404 | User không tồn tại |

### Auth

| Code | Status | Khi nào | Message hiện tại |
|---|---|---|---|
| `INVALID_CREDENTIALS` | 401 | `POST /auth/login`: email không tồn tại hoặc mật khẩu sai (cùng một thông báo) | Email hoặc mật khẩu không đúng |
| `ACCOUNT_DISABLED` | 403 | `POST /auth/login`: đúng mật khẩu nhưng tài khoản bị vô hiệu hóa | Tài khoản đã bị vô hiệu hoá |
| `UNAUTHORIZED` | 401 | Thiếu header `Authorization` hoặc không phải Bearer | Bạn chưa đăng nhập |
| `UNAUTHORIZED` | 401 | Token sai chữ ký, hết hạn, thiếu `sub`; hoặc user không còn tồn tại, bị vô hiệu hóa | Phiên đăng nhập không hợp lệ hoặc đã hết hạn |
| `FORBIDDEN` | 403 | Vai trò không nằm trong danh sách cho phép của endpoint | Bạn không có quyền thực hiện thao tác này |

Lưu ý cho client:

- Chỉ code `UNAUTHORIZED` mới nên khiến client xóa token và chuyển về trang đăng nhập.
  `INVALID_CREDENTIALS` là lỗi của chính form đăng nhập, không được chuyển hướng
  (tránh vòng lặp).
- `ACCOUNT_DISABLED` chỉ xuất hiện lúc đăng nhập. Với token đang dùng, tài khoản bị
  khóa nhận `UNAUTHORIZED`.
- Chi tiết luồng và ma trận quyền: xem `docs/auth-flow.md`.

## 4. Lỗi validation (422)

Hiện tại FastAPI trả định dạng mặc định, **khác** định dạng ở mục 1:

    { "detail": [ { "loc": ["body", "title"], "msg": "...", "type": "..." } ] }

Ở lỗi nghiệp vụ `detail` là **object**, ở lỗi 422 `detail` là **mảng**. Client phải
xử lý hai kiểu. Đề xuất chuẩn hóa:

    {
      "detail": {
        "code": "VALIDATION_ERROR",
        "message": "Dữ liệu không hợp lệ",
        "errors": [ { "field": "body.title", "message": "..." } ]
      }
    }

Cách làm: đăng ký thêm `RequestValidationError` handler trong `main.py`.
**Trạng thái: đề xuất, chưa áp dụng.**

## 5. Quy tắc riêng cho dữ liệu hai kho (SQL và Mongo)

- SQL là nguồn sự thật. Bài chỉ hiển thị khi `status = published`.
- Trạng thái bài: `pending` (đang ghi), `published`, `failed` (Mongo lỗi lúc tạo).
- `CONTENT_MISSING`: bài có ở SQL nhưng thiếu nội dung ở Mongo. Thử lại không giúp
  ích, cần dọn hoặc đối soát dữ liệu. Server ghi log mức ERROR.
- `STORE_UNAVAILABLE`: lỗi tạm thời, client có thể thử lại sau.
- Không bao giờ để một bài `published` mà thiếu nội dung do lỗi lúc tạo: nếu bước
  xác nhận thất bại thì nội dung Mongo bị xóa bù trừ.

## 6. Hướng dẫn cho client (UI)

| Tình huống | Hiển thị |
|---|---|
| Đang gọi API | Trạng thái loading |
| Danh sách rỗng (`items = []`) | Trạng thái empty |
| 404 (`*_NOT_FOUND`) | Trạng thái not found |
| 503 `STORE_UNAVAILABLE`, 500 | Trạng thái lỗi kèm nút thử lại |
| 500 `CONTENT_MISSING` | Trạng thái lỗi, không có nút thử lại |
| 401 | Chuyển về trang đăng nhập |
| 403 | Thông báo không đủ quyền |
| 409 | Thông báo xung đột kèm `message` |
EOF