import sys
import os
sys.path.append(os.getcwd())
from backend.app.core.config import settings

print(f"User: {settings.POSTGRES_USER}")
print(f"Password: {settings.POSTGRES_PASSWORD}")
print(f"DB: {settings.POSTGRES_DB}")
print(f"URI: {settings.SQLALCHEMY_DATABASE_URI}")
