
import os

SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
JWT_SECRET        = os.environ.get("JWT_SECRET", "mentor-mind-secret-key")
JWT_ALGORITHM     = "HS256"
JWT_EXPIRE_MINS   = int(os.environ.get("JWT_EXPIRE_MINS", "60"))
MIN_PASSWORD_LENGTH = 6
