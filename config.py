from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

MONGO_URL = os.environ.get("MONGO_URL")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET")
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_REGION = os.environ.get("S3_REGION")

print(S3_KEY, S3_SECRET)