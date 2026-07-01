import os
import logging
import warnings
import traceback
from datetime import datetime

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("MentorMind")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="MENTOR MIND AI",
    description="Multi-Agent Learning System",
    version="9.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── GLOBAL ERROR HANDLER — shows real traceback ───────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    log.error("UNHANDLED ERROR on " + str(request.url.path) + ": " + str(exc))
    log.error(tb)
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "path": str(request.url.path),
            "type": type(exc).__name__,
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now()
    try:
        response = await call_next(request)
        duration = (datetime.now() - start).total_seconds()
        log.info(request.method + " " + request.url.path + " -> " + str(response.status_code) + " (" + str(round(duration,2)) + "s)")
        return response
    except Exception as e:
        log.error("Middleware caught error: " + str(e))
        traceback.print_exc()
        raise


# ── INITIALIZE EVERYTHING WITH ERROR HANDLING ─────────
log.info("Initializing MENTOR MIND AI...")

try:
    from mentor_mind.database.db_setup import create_tables
    from mentor_mind.memory.persistent import PersistentMemory

    create_tables()
    memory = PersistentMemory()
    log.info("Database + Memory ready")
except Exception as e:
    log.error("DATABASE INIT FAILED: " + str(e))
    traceback.print_exc()
    raise

try:
    from mentor_mind.agents.teacher_agent import TeacherAgent
    from mentor_mind.agents.planner_agent import PlannerAgent
    from mentor_mind.agents.memory_agent import MemoryAgent
    from mentor_mind.agents.tester_agent import TesterAgent
    from mentor_mind.agents.scheduler_agent import SchedulerAgent
    from mentor_mind.agents.general_agent import GeneralAgent

    teacher = TeacherAgent(memory)
    planner = PlannerAgent(memory)
    mem_agent = MemoryAgent(memory)
    tester = TesterAgent(memory)
    scheduler = SchedulerAgent(memory)
    general = GeneralAgent(memory)
    log.info("All 6 sub-agents ready")
except Exception as e:
    log.error("AGENTS INIT FAILED: " + str(e))
    traceback.print_exc()
    raise

rag_engine = None
rag_agent = None
try:
    from mentor_mind.rag.rag_engine import RAGEngine
    from mentor_mind.rag.rag_agent import RAGAgent
    rag_engine = RAGEngine()
    rag_agent = RAGAgent(memory, rag_engine)
    log.info("RAG Agent loaded")
except Exception as e:
    log.warning("RAG not available: " + str(e))

try:
    from mentor_mind.agents.coordinator_v3 import CoordinatorAgent
    coordinator = CoordinatorAgent(memory)
    log.info("Coordinator ready")
except Exception as e:
    log.error("COORDINATOR INIT FAILED: " + str(e))
    traceback.print_exc()
    raise

log.info("MENTOR MIND AI fully initialized!")


def build_response(result: dict) -> str:
    parts = []
    if "plan" in result:
        p = result["plan"]
        parts.append("Study Plan: " + p["topic"] + " (" + str(p["total_days"]) + " days)")
        for d in p.get("schedule", []):
            parts.append("Day " + str(d["day"]) + ": " + d["task"])
        parts.append("")
    for key in ["teaching", "memory", "today", "schedule", "general"]:
        if key in result:
            parts.append(result[key])
    if "quiz" in result:
        q = result["quiz"]
        parts.append("Quiz: " + q["topic"])
        for x in q.get("questions", []):
            parts.append("Q" + str(x["id"]) + ": " + x["question"])
            for k, v in x["options"].items():
                parts.append("  " + k + ") " + v)
            parts.append("  Answer: " + x["answer"] + " - " + x["explanation"])
    for k, v in result.items():
        if k.endswith("_error"):
            parts.append("Warning: " + str(v))
    if not parts:
        parts.append("Hi! I am MENTOR MIND AI. Ask me anything!")
    return "\n".join(parts)


# ── ROUTES — wrapped in try/except ────────────────────
try:
    from mentor_mind.api.routes.auth import router as auth_router
    app.include_router(auth_router)
    log.info("Auth routes loaded")
except Exception as e:
    log.error("AUTH ROUTES FAILED: " + str(e))
    traceback.print_exc()

try:
    from mentor_mind.api.routes.chat import router as chat_router
    app.include_router(chat_router)
    log.info("Chat routes loaded")
except Exception as e:
    log.error("CHAT ROUTES FAILED: " + str(e))
    traceback.print_exc()

try:
    from mentor_mind.api.routes.history import router as history_router
    app.include_router(history_router)
    log.info("History routes loaded")
except Exception as e:
    log.error("CHAT ROUTES FAILED: " + str(e))
    traceback.print_exc()

try:
    from mentor_mind.api.routes.progress import router as progress_router
    app.include_router(progress_router)
    log.info("Progress routes loaded")
except Exception as e:
    log.warning("Progress routes not loaded: " + str(e))

try:
    from mentor_mind.api.routes.documents import router as documents_router
    app.include_router(documents_router)
    log.info("Documents routes loaded")
except Exception as e:
    log.warning("Documents routes not loaded: " + str(e))

try:
    from mentor_mind.api.routes.tools import router as tools_router
    app.include_router(tools_router)
    log.info("Tools routes loaded")
except Exception as e:
    log.warning("Tools routes not loaded: " + str(e))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    try:
        from mentor_mind.api.templates_html import HTML_CONTENT
        return HTML_CONTENT
    except Exception as e:
        log.error("HOME PAGE FAILED: " + str(e))
        traceback.print_exc()
        return HTMLResponse(
            content="<h1>Error loading page</h1><p>" + str(e) + "</p><pre>" + traceback.format_exc() + "</pre>",
            status_code=500
        )


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "version": "9.0.0",
        "timestamp": datetime.now().isoformat(),
    }
