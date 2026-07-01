import os
import sys

print("=== STARTUP DEBUG ===")
print("Working directory:", os.getcwd())
print("Contents:", os.listdir("."))
print("sys.path:", sys.path)

if os.path.isdir("mentor_mind"):
    print("mentor_mind FOLDER FOUND")
    print("mentor_mind contents:", os.listdir("mentor_mind"))
else:
    print("mentor_mind FOLDER NOT FOUND AT RUNTIME!")

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "mentor_mind.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
