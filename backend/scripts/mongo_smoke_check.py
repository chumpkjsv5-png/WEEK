from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["myapp"]
users = db["users"]

# # Thêm
# result = users.insert_one({"name": "Vincent", "email": "vincent@example.com"})
# print(result.inserted_id)

# # Tìm
# print(users.find_one({"name": "Vincent"}))
# for u in users.find():
#     print(u)

# Sửa
users.update_one({"name": "Vincent"}, {"$set": {"age": 28}})

# # Xóa
# users.delete_one({"name": "Vincent"})