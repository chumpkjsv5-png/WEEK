# Week 1 Task API

Task Management API xây dựng bằng FastAPI + SQLAlchemy + PostgreSQL (Neon).

## Tính năng

- Tạo, sửa, hoàn thành, xoá task (Create / Edit / Finish / Delete)
- Xem, tìm kiếm, lọc task theo trạng thái (View / Search / Filter)
- Dữ liệu lưu trong PostgreSQL, giữ nguyên sau khi refresh
- Validate dữ liệu đầu vào bằng Pydantic, trả lỗi 4xx rõ ràng khi input sai

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── main.py              # Khởi tạo app, gắn router
│   ├── database.py          # Kết nối PostgreSQL (Neon)
│   ├── models/
│   │   └── task_data.py     # Định nghĩa bảng tasks (SQLAlchemy model)
│   ├── schemas/
│   │   └── task_schema.py   # Validate dữ liệu vào/ra (Pydantic)
│   ├── services/
│   │   └── task_service.py  # Logic xử lý nghiệp vụ (CRUD)
│   └── routers/
│       └── task_router.py   # Định nghĩa endpoint (routes)
├── requirements.txt
└── .env                     # Biến môi trường (không commit lên git)
```

## Yêu cầu môi trường

- Python 3.10+
- Tài khoản Neon (PostgreSQL serverless) hoặc PostgreSQL bất kỳ

## Cài đặt

### 1. Clone repo

```bash
git clone <link-repo-cua-ban>
cd backend
```

### 2. Tạo virtual environment

```bash
python -m venv .venv
```

### 3. Kích hoạt virtual environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 4. Cài thư viện

```bash
pip install -r requirements.txt
```

### 5. Tạo file `.env`

Tạo file `.env` ở thư mục gốc `backend/` với nội dung:

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require&channel_binding=require
```

Thay các giá trị `<user>`, `<password>`, `<host>`, `<database>` bằng thông tin connection string thật lấy từ Neon Console.

### 6. Chạy server

```bash
uvicorn app.main:app --reload
```

Nếu thành công, terminal hiện:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 7. Kiểm tra

Mở trình duyệt:
```
http://127.0.0.1:8000/docs
```

Đây là Swagger UI — giao diện test API tự động, có thể thử trực tiếp không cần Postman.

## API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/tasks/` | Tạo task mới |
| GET | `/tasks/` | Lấy danh sách task (hỗ trợ `search`, `status`, `assignee_id`) |
| GET | `/tasks/{id}` | Lấy chi tiết 1 task |
| PUT | `/tasks/{id}` | Cập nhật task |
| PATCH | `/tasks/{id}/complete` | Đánh dấu task hoàn thành |
| DELETE | `/tasks/{id}` | Xoá task |

Chi tiết đầy đủ (request/response schema) xem tại `/docs`.

## Xử lý lỗi

- Dữ liệu đầu vào sai định dạng → trả về `422 Unprocessable Entity` kèm chi tiết field lỗi
- Task không tồn tại (edit/delete/complete) → trả về `404 Not Found`

## Ghi chú

- File `.env` chứa thông tin nhạy cảm, **không commit lên git** (đã có trong `.gitignore`)
- Bảng `tasks` tự động được tạo khi chạy server lần đầu (`Base.metadata.create_all()`)
