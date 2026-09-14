import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://127.0.0.1:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "finsight")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
