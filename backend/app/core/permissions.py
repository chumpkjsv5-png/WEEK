# app/core/permissions.py
ADMIN = "admin"
MANAGER = "manager"
MEMBER = "member"

CAN_MANAGE = (ADMIN, MANAGER)   # tạo/sửa project, task
ADMIN_ONLY = (ADMIN,)