import base64, hashlib, hmac, os, time
from itsdangerous import URLSafeSerializer
from app.core.config import SECRET_KEY
serializer = URLSafeSerializer(SECRET_KEY, salt="finsight-auth")
def hash_password(password: str) -> str:
    salt=os.urandom(16); key=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1); return base64.b64encode(salt+key).decode()
def verify_password(password: str, encoded: str) -> bool:
    raw=base64.b64decode(encoded.encode()); salt,expected=raw[:16],raw[16:]; actual=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1); return hmac.compare_digest(actual,expected)
def create_token(user_id: str, role: str) -> str: return serializer.dumps({"sub":str(user_id),"role":role,"iat":int(time.time())})
def decode_token(token: str) -> dict: return serializer.loads(token)
