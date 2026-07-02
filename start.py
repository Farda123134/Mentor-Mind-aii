import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=== STARTUP DIAGNOSTICS ===")
print("Script location:", current_dir)
print("Working directory:", os.getcwd())
print("Contents of script directory:", os.listdir(current_dir))

mentor_mind_path = os.path.join(current_dir, "mentor_mind")
if os.path.isdir(mentor_mind_path):
    print("mentor_mind FOUND at:", mentor_mind_path)
else:
    print("mentor_mind NOT FOUND at expected path:", mentor_mind_path)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "mentor_mind.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
