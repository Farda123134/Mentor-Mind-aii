import os
import sys

# Debug: confirm current directory aur mentor_mind ki location
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir("."))
print("Python path:", sys.path)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "mentor_mind.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
