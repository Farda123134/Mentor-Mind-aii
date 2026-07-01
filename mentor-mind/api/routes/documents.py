
import os
import logging
import traceback

from fastapi           import APIRouter, UploadFile, File, Form, HTTPException
from mentor_mind.api.models.schemas import UploadResponse

log    = logging.getLogger("MentorMind")
router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_FOLDER      = "./uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_docx_text(path: str) -> str:
    """DOCX se text nikalo."""
    try:
        from docx import Document
        doc  = Document(path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text
    except Exception as e:
        log.error("DOCX extraction error: " + str(e))
        return ""


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file       : UploadFile = File(...),
    session_id : str        = Form(...),
    topic      : str        = Form(default="")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, TXT, MD files allowed"
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        log.info("File saved: " + file_path)
    except Exception as e:
        log.error("File save error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not save file")

    try:
        from mentor_mind.api.main import rag_engine

        if not rag_engine:
            return UploadResponse(
                success  = True,
                message  = file.filename + " uploaded (RAG search not available)",
                filename = file.filename
            )

        ext = file.filename.rsplit(".", 1)[1].lower()

        if ext == "docx":
            text   = extract_docx_text(file_path)
            doc_id = session_id + "_" + file.filename
            from mentor_mind.rag.rag_engine import RAGEngine
            success = rag_engine.add_document(
                text, doc_id,
                metadata={"session_id": session_id, "file_name": file.filename, "topic": topic}
            )
            result = {
                "success": success,
                "message": ("✅ " + file.filename + " uploaded!") if success else "Processing failed",
                "chunks_count": 0,
                "doc_id": doc_id
            }
        else:
            result = rag_engine.add_file(file_path, session_id, topic)

        return UploadResponse(
            success      = result.get("success", False),
            message      = result.get("message", ""),
            filename     = file.filename,
            chunks_count = result.get("chunks_count", 0),
            doc_id       = result.get("doc_id", "")
        )

    except Exception as e:
        log.error("RAG add failed: " + str(e))
        traceback.print_exc()
        return UploadResponse(
            success  = True,
            message  = file.filename + " uploaded but indexing failed",
            filename = file.filename
        )


@router.get("/list/{session_id}")
async def list_documents(session_id: str):
    try:
        from mentor_mind.api.main import rag_engine
        if rag_engine:
            docs = rag_engine.list_documents(session_id)
            return {"session_id": session_id, "documents": docs, "count": len(docs)}
        return {"session_id": session_id, "documents": [], "count": 0}
    except Exception as e:
        log.error("List documents error: " + str(e))
        raise HTTPException(status_code=500, detail="Could not list documents")


@router.delete("/{session_id}/{doc_id}")
async def delete_document(session_id: str, doc_id: str):
    try:
        from mentor_mind.api.main import rag_engine
        if rag_engine:
            success = rag_engine.delete_document(doc_id, session_id)
            return {"success": success, "doc_id": doc_id}
        return {"success": False, "message": "RAG not available"}
    except Exception as e:
        log.error("Delete document error: " + str(e))
        raise HTTPException(status_code=500, detail=str(e))
