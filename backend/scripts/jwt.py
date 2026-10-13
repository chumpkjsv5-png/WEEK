# import jwt
# import json

# token = jwt.encode({"sub": "123"}, "secret", algorithm="HS256")

# print("JWT:", token)

# # Tách thành 3 phần
# header, payload, signature = token.split(".")

# print("\nHeader:", header)
# print("Payload:", payload)
# print("Signature:", signature)

# # Giải mã Header và Payload để đọc nội dung
# print("\nHeader JSON:", jwt.get_unverified_header(token))
# print("Payload JSON:", jwt.decode(token, options={"verify_signature": False}))

import hmac
import hashlib
import base64

message = "abc.xyz"
secret_key = "my-secret"

signature_bytes = hmac.new(
    secret_key.encode(),
    message.encode(),
    hashlib.sha256
).digest()

signature = base64.urlsafe_b64encode(
    signature_bytes
).rstrip(b"=").decode()

print(signature)