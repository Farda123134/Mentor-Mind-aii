
# ═══════════════════════════════════════════════════════
# TOOLS ROUTES
# Direct tool calling endpoints
# ═══════════════════════════════════════════════════════

import logging
from fastapi  import APIRouter, HTTPException
from ..models.schemas import ToolRequest, ToolResponse

log    = logging.getLogger("MentorMind")
router = APIRouter(
    prefix = "/tools",
    tags   = ["Tools"]
)


# ── POST /tools/run ───────────────────────────────────
@router.post(
    "/run",
    response_model = ToolResponse,
    summary        = "Run a specific tool",
    description    = "Directly kisi tool ko call karo."
)
async def run_tool(request: ToolRequest):
    """
    Tool directly run karo.

    Tools:
    - calculator  : Math expressions
    - datetime    : Date/time queries
    - code_runner : Python code execute
    - web_search  : Web search
    """
    try:
        from mentor_mind.tools.tool_manager import ToolManager

        tm     = ToolManager()
        result = tm.run_tool(request.tool, request.input)

        return ToolResponse(
            tool    = request.tool,
            input   = request.input,
            output  = result.get("output", ""),
            success = result.get("success", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /tools/list ───────────────────────────────────
@router.get(
    "/list",
    summary     = "List available tools",
    description = "Sare available tools ki list."
)
async def list_tools():
    """Available tools dekho."""
    try:
        from mentor_mind.tools.tool_manager import ToolManager

        tm    = ToolManager()
        tools = tm.list_tools()
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /tools/auto ──────────────────────────────────
@router.post(
    "/auto",
    summary     = "Auto-detect and run tool",
    description = "Query se automatically sahi tool detect karke run karo."
)
async def auto_tool(query: str):
    """
    Query bhejo — automatically sahi tool detect aur run hoga.
    """
    try:
        from mentor_mind.tools.tool_manager import ToolManager

        tm     = ToolManager()
        result = tm.process_with_tools(query)

        return {
            "query"    : query,
            "used_tool": result["used_tool"],
            "tool"     : result.get("tool"),
            "output"   : result.get("output_text", "No tool needed"),
            "success"  : result.get("success", True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
