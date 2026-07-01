"""
Entry point for production deployment.
Render/Railway/Fly.io yeh file run karenge.
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "mentor_mind.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
